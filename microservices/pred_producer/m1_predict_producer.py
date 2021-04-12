from kafka import KafkaProducer
import torch
import json
from foobar.model.lstm import LSTM
from foobar.model.model_loader import download_model
from foobar.db_utils.cassandra_utils import query_table
from foobar.prediction.predictor import prediction
import os
import pandas as pd
import numpy as np
import uuid
# testing the producer with csv data
# import pandas as pd
# df_gamestop = pd.read_csv('microservices/m1_pred_producer/sample.csv')
# import time
# while True: time.sleep(10000)

GAMESTOP_TABLE = (
    os.environ.get("GAMESTOP_TABLE") if os.environ.get("GAMESTOP_TABLE") else "gamestop"
)
TIMESTAMP_COLUMN = "timestamp_"

BUCKET = (
    os.environ.get("BUCKET_NAME")
    if os.environ.get("BUCKET_NAME")
    else "bb-s3-bucket-cmpt733"
)
MODEL_FILE = "m1.pth"
LOCAL_FILE = MODEL_FILE

# Kafka producer
KAFKA_BROKER_URL = (
    os.environ.get("KAFKA_BROKER_URL")
    if os.environ.get("KAFKA_BROKER_URL")
    else "localhost:9092"
)
TOPIC_NAME = (
    os.environ.get("TOPIC_NAME") if os.environ.get("TOPIC_NAME") else "from_finnhub"
)
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 300))

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER_URL,
    value_serializer=lambda x: x.encode("utf8"),
    api_version=(0, 11, 5),
)


# read historical data from cassandra and make predictions
try:
    train_result = download_model(BUCKET, MODEL_FILE, LOCAL_FILE)
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

    df_gamestop = query_table(GAMESTOP_TABLE)
    print("queried gamestop table")

    if df_gamestop is not None:
        print(df_gamestop.head())
        df_predictions = prediction(
            model, device, train_scaler, df_gamestop, train_parameter_set
        )
        # df_predictions.to_csv('microservices/m1_pred_producer/sample.csv')
        if df_predictions is not None:
            df_predictions.rename({'id': 'uuid'}, axis=1, inplace=True)
            df_predictions.drop('prediction', axis=1, inplace=True)
            df_predictions['uuid'] = str(uuid.uuid4())
            df_predictions['timestamp_'] = pd.to_datetime(df_predictions['timestamp_'], unit="s")
            df_predictions['timestamp_'] = df_predictions['timestamp_'].dt.strftime("%Y-%m-%d %H:%M:%S")
            df_predictions['close_price_pred'] = df_predictions['close_price']
            print(df_predictions['close_price_pred'])
            print("Sending prediction records to kafka")

            for index, row in df_predictions.iterrows():
                if index > 30: break
                print(row.to_json())
                producer.send(TOPIC_NAME, value=row.to_json())
    print("Done with predictions...")

except Exception as e:
    print(f"prediction failed. ERROR: {e}")

