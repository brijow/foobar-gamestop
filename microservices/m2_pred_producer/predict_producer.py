from kafka import KafkaProducer
import time
from datetime import datetime, timedelta
import torch
import json
from foobar.model.lstm import LSTM
from foobar.model.model_loader import download_model
from foobar.db_utils.cassandra_utils import query_table
import os

# testing the producer with csv data
# import pandas as pd
# df_gme = pd.read_csv("foobar/data/processed/gme.csv")

WIDE_TABLE = os.environ.get("WIDE_TABLE") if os.environ.get("WIDE_TABLE") else "wide"

TIMESTAMP_COLUMN = "timestamp_"

BUCKET = os.environ.get("BUCKET_NAME") if os.environ.get("BUCKET_NAME") else "bb-s3-bucket-cmpt733"
MODEL_FILE = "m2.pth"
LOCAL_FILE = MODEL_FILEervices/m2_pred_producer/m2.pth"

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
    value_serializer=lambda x: json.dumps(x).encode("utf8"),
    api_version=(0, 11, 5),
)
# read historical data from cassandra and make predictions

last_poll_datetime = datetime.utcnow() - timedelta(hours=100)

while True:
    try:
        train_result = download_model(BUCKET, MODEL_FILE, LOCAL_FILE)
        # extract model parameters
        feature_set = train_result["feature_set"]
        history = train_result["history"]
        prediction_horizon = int(train_result["pred_horizon"])
        train_window = int(train_result["train_window"])
        train_scaler = train_result["scaler"]

        num_features = len(feature_set) - 1
        device = torch.device("cpu")
        model = LSTM(input_size=num_features, seq_length=train_window)
        model.load_state_dict(train_result["model"])

        query_from = last_poll_datetime
        query_to = query_from + timedelta(hours=train_window)
        df_gme = query_table(WIDE_TABLE, TIMESTAMP_COLUMN,query_from, query_to)
        print(f"queried gme table from {query_from} to {query_to}")

        if df_gme is not None and not df_gme.empty:
            # feature_set = ['openprice', 'highprice', 'lowprice', 'volume', 'closeprice']
            gme_scaled = train_scaler.transform(df_gme[feature_set])
            x = (
                torch.tensor(gme_scaled[:train_window, :num_features])
                .float()
                .reshape(1, train_window, num_features)
            )
            # print(x.shape)

            with torch.no_grad():
                model.eval()
                x.to(device)
                model.init_hidden(1, device)
                y_pred = model(x)
                close_price_pred = y_pred.item()
                print(f"Next hour close price predicted: {close_price_pred}")
                prediction_dict = {
                    "close_price_predict": close_price_pred,
                    "timestamp_": query_to
                    + timedelta(hours=prediction_horizon),
                }
                producer.send(TOPIC_NAME, value=prediction_dict)

        print("Next prediction...")
        last_poll_datetime = query_to

    except Exception as e:
        print(f"prediction failed. ERROR: {e}")

    time.sleep(SLEEP_TIME)
