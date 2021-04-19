import time
from datetime import datetime, timedelta
import os
import json
import boto3
import pandas as pd
from kafka import KafkaProducer
import torch
import sys
from foobar.model.lstm import LSTM
from foobar.model.model_loader import download_model
from foobar.db_utils.cassandra_utils_v2 import *
from foobar.db_utils.cassandra_utils import query_table, query_table_for_hour, get_tags_by_postids
from foobar.db_utils.operations import get_aggregates_by_hour, build_wide_table
from m1_predict_producer import FinnHubPredictor
from foobar.prediction.predictor import prediction

BUCKET_NAME = (
    os.environ.get("BUCKET_NAME")
    if os.environ.get("BUCKET_NAME")
    else "bb-s3-bucket-cmpt733"
)

KAFKA_ENABLED=os.environ.get("KAFKA_ENABLED", "true") == "true"

# Kafka producer
KAFKA_BROKER_URL = (
    os.environ.get("KAFKA_BROKER_URL")
    if os.environ.get("KAFKA_BROKER_URL")
    else "localhost:9092"
)


GAMESTOP_TABLE = os.environ.get("GAMESTOP_TABLE", "gamestop")

POSTS_TABLE = os.environ.get("POSTS_TABLE", "post")

TAG_TABLE = os.environ.get("TAG_TABLE", "tag")

WIDE_TABLE = os.environ.get("WIDE_TABLE", "wide")

TOPIC_NAME = os.environ.get("TOPIC_NAME", "wide")


class WideTablePredictor:
    def __init__(self):
        session = boto3.Session(
                    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=os.environ['AWS_SECRET_KEY'],
                    region_name=os.environ['REGION_NAME'])
                    
        s3 = session.resource('s3')
        self.bucket = s3.Bucket(BUCKET_NAME)
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER_URL,
            value_serializer=lambda x: x.encode("utf8"),
            api_version=(0, 11, 5),
        )
        self.model_file = "m2.pth"
        self.local_file = self.model_file
        self.finnhubpredictor = FinnHubPredictor(GAMESTOP_TABLE, bucket=self.bucket)

    def runWidePredictionProcess(self):
        now = datetime.now()
        print("{} Starting Wide prediction process".format(now.strftime("%Y-%m-%d %H:%M:%S")))
        predictions = self.makeWidePredictions()
        if predictions is None:
            print("{} Did not receive any wide table predictions".format(now.strftime("%Y-%m-%d %H:%M:%S")))
            return
        if KAFKA_ENABLED:
            print(f"Finished prediction of {len(predictions)} rows. Now sending it to Kafka")
            self.sendRecordstoKafka(predictions)
        else:
            print(f"KAFKA DISABLED* Finished prediction of {len(predictions)} rows. Would have sent to Kafka now")
        now = datetime.now()
        print("{} Wide prediction process done".format(now.strftime("%Y-%m-%d %H:%M:%S")))

    def getFinnhubPredictions(self, wide_df):
        gamestop_df = wide_df[GAMESTOP_COLS]
        return self.finnhubpredictor.predictNewData(gamestop_df)


    def obtainWide_df(self):
        wide_df = run_wide_row_builder()
        if wide_df is None or wide_df.empty:
            return None
        return wide_df.sort_values("hour")

    def makeWidePredictions(self):        
        try:
            print("Running wide prediction model")
            train_result = download_model(self.bucket, self.model_file, self.local_file)
            # extract model parameters
            feature_set = train_result["feature_set"]
            prediction_horizon = int(train_result["pred_horizon"])
            train_window = int(train_result["train_window"])
            train_scaler = train_result["scaler"]

            feature_set.append('prediction_wide')
            train_parameter_set = (feature_set, train_window, prediction_horizon, "prediction_wide")

            num_features = len(feature_set)-1
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model = LSTM(input_size=num_features, seq_length=train_window)
            model.load_state_dict(train_result["model"])
            
            # wide_df = pd.read_csv("wide.csv")
            wide_df = self.obtainWide_df()
            if wide_df is None or wide_df.empty:
                print("Did not get any wide df data")
                return None

            predictedFinnhub = self.getFinnhubPredictions(wide_df[GAMESTOP_COLS])
            
            wide_df = wide_df.rename(
                columns={
                    "close_price": "closeprice",
                    "open_price": "openprice",
                    "high_price": "highprice",
                    "low_price": "lowprice",
                }
            )
            df_predictions = prediction(
                model, device, None, wide_df, train_parameter_set
            )
            df_predictions = df_predictions.drop(['prediction_finn', 'volume', 'openprice', 'highprice', 'lowprice', 'closeprice'], axis=1)
            newpredictions = pd.merge(predictedFinnhub, df_predictions, on='hour')

            print("Done with Wide predictions from {} to {}".format(newpredictions['hour'].min(), newpredictions['hour'].max()))
            # newpredictions['hour'] = pd.to_datetime(newpredictions['hour'], unit="s")+ pd.to_timedelta(10, unit='s')
            
            newpredictions['hour'] = pd.date_range('today', periods=len(newpredictions), freq='S')
            newpredictions['hour'] = newpredictions['hour'].dt.strftime("%Y-%m-%d %H:%M:%S")
            newpredictions=newpredictions.reset_index()
            return newpredictions[WIDE_COLS]


        except Exception as e:
            print(f"prediction failed. ERROR: {e}")
    
    def sendRecordstoKafka(self, df):
        print(f"Going to send {len(df)} records to kafka")
        for index, row in df.iterrows():
            print(row.to_json())
            self.producer.send(TOPIC_NAME, value=row.to_json())
        self.producer.flush()

if __name__ == "__main__":
    widepredictor = WideTablePredictor()
    widepredictor.runWidePredictionProcess()