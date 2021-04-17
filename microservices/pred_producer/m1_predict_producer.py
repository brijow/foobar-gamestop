import torch
import json
from foobar.model.lstm import LSTM
from foobar.model.model_loader import download_model
from foobar.db_utils.cassandra_utils import query_table
from foobar.prediction.predictor import prediction
import os
import pandas as pd
import numpy as np
import boto3
# testing the producer with csv data
# import pandas as pd
# df_gamestop = pd.read_csv('microservices/m1_pred_producer/sample.csv')
# import time
# while True: time.sleep(10000)


class FinnHubPredictor:
    def __init__(self,
                gamestop_table : str,
                bucket_name : str,
                bucket=None) :
        self.MODEL_FILE = "m1.pth"
        self.LOCAL_FILE = self.MODEL_FILE
        self.TIMESTAMP_COLUMN = "hour"
        self.GAMESTOP_TABLE = gamestop_table
        self.BUCKET_NAME = bucket_name
        if bucket is None:
            session = boto3.Session(
                        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                        aws_secret_access_key=os.environ['AWS_SECRET_KEY'],
                        region_name=os.environ['REGION_NAME'])
                        
            s3 = session.resource('s3')
            self.bucket = s3.Bucket(bucket_name)
        else:
            self.bucket = bucket

    def predictNewData(self, newdata_df=None, historicaldata_=None):
        if historicaldata_ is None:
            historicaldata_ = query_table(self.GAMESTOP_TABLE)
        print("queried gamestop table")
        if newdata_df is not None:
            print("Merging new data with historical data")
            data_ = pd.concat([historicaldata_, newdata_df], axis=0)
        newpredictionids = data_[data_['close_price_pred'] == -1]
        predictions = self.producePredictions(data_)
        if predictions is None : return None
        newpredictions = predictions[predictions['id'] == newpredictionids['id']]
        return newpredictions

    def producePredictions(self, df_gamestop : pd.DataFrame):
        # read historical data from cassandra and make predictions
        print("Running prediction model")
        try:
            train_result = download_model(self.bucket, self.BUCKET_NAME, self.MODEL_FILE, self.LOCAL_FILE)
            # extract model parameters
            feature_set = train_result["feature_set"]
            history = train_result["history"]
            prediction_horizon = int(train_result["pred_horizon"])
            train_window = int(train_result["train_window"])
            train_scaler = train_result["scaler"]
            train_parameter_set = (feature_set, train_window, prediction_horizon)

            num_features = len(feature_set) - 1
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model = LSTM(input_size=num_features, seq_length=train_window)
            model.load_state_dict(train_result["model"])

            if df_gamestop is not None:
                print(df_gamestop.head())
                df_predictions = prediction(
                    model, device, train_scaler, df_gamestop, train_parameter_set
                )
                # df_predictions.to_csv('microservices/m1_pred_producer/sample.csv')
            print("Done with predictions...")
            return df_predictions
        except Exception as e:
            print(f"prediction failed. ERROR: {e}")
            return None

if __name__ == '__main__':
    print("Starting Finhub prediction runner")
    predictor = FinnHubPredictor()
    newrows = predictor.predictNewData()
    print(f"Predicted {len(newrows)} new rows.")
    print(newrows)