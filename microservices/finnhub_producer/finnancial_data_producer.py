import configparser
import json
import os
import time
from datetime import datetime, timedelta

import finnhub
import pandas as pd
from kafka import KafkaProducer
import uuid

# Finnhub API config
AUTH_TOKEN = os.environ.get("FINNHUB_AUTH_TOKEN")
if AUTH_TOKEN is None:
    config = configparser.ConfigParser()
    config.read("foobar/data_loader/conf/finnhub.cfg")
    api_credential = config["api_credential"]

SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 300))

# Kafka producer
KAFKA_BROKER_URL = (
    os.environ.get("KAFKA_BROKER_URL")
    if os.environ.get("KAFKA_BROKER_URL")
    else "localhost:9092"
)
TOPIC_NAME = (
    os.environ.get("TOPIC_NAME") if os.environ.get("TOPIC_NAME") else "from_finnhub"
)


class finnhub_producer:

    # _last_poll_datetime = datetime.utcnow()
    # print(_last_poll_datetime)
    def __init__(self, api_token):
        self.last_poll_datetime = datetime.utcnow() - timedelta(minutes=500)
        # _last_poll_datetime = datetime.utcnow()
        # print(_last_poll_datetime)
        self.api_client = finnhub.Client(api_key=api_token)
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER_URL,
            value_serializer=lambda x: x.encode("utf8"),
            api_version=(0, 11, 5),
        )

    def query_stock_candles(self, symbol, date_from, date_to):

        from_ts = int(datetime.timestamp(date_from))
        to_ts = int(datetime.timestamp(date_to))

        out = self.api_client.stock_candles(
            symbol=symbol, resolution="5", _from=from_ts, to=to_ts
        )
        if out["s"] == "no_data":
            print("no data")
            return
        else:
            df = pd.DataFrame(out)
            df = df.rename(
                columns={
                    "c": "close_price",
                    "o": "open_price",
                    "h": "high_price",
                    "l": "low_price",
                    "v": "volume",
                    "t": "timestamp_",
                    "s": "status",
                }
            )
            stock_candle_timeseries = df.reset_index()#.set_index("timestamp")
            return stock_candle_timeseries

    def run(self):
        date_from = self.last_poll_datetime
        date_to = datetime.utcnow()
        print(f'Getting stock price from {date_from} to {date_to}')
        ts = self.query_stock_candles(
            symbol="GME", date_from=date_from, date_to=date_to
        )
        if ts is not None:
            print('Sending financial data to Kafka queue...')
            ts['timestamp_'] = pd.to_datetime(ts['timestamp_'], unit="s")
            ts['timestamp_'] = ts['timestamp_'].dt.strftime("%Y-%m-%d %H:%M:%S")
            for index, row in ts.iterrows():
                row['uuid'] = str(uuid.uuid4())
                print(row.to_json())
                self.producer.send(TOPIC_NAME, value=row.to_json())
            self.producer.flush()
            print(f'Stock price from {date_from} to {date_to} was sent to Kafka')
        time.sleep(SLEEP_TIME)
        self.last_poll_datetime = date_to


if __name__ == "__main__":
    print("Starting Finnhub producer")
    finnhub_service = finnhub_producer(api_token=AUTH_TOKEN)
    while True:
        finnhub_service.run()