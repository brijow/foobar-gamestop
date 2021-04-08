import configparser
import json
import os
import time
from datetime import datetime, timedelta

import finnhub
import pandas as pd
from kafka import KafkaProducer

# Finnhub API config
config = configparser.ConfigParser()
config.read("foobar/data_loader/conf/finnhub.cfg")
api_credential = config["api_credential"]
AUTH_TOKEN = api_credential["auth_token"]

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
                    "h": "high-price",
                    "l": "low-price",
                    "v": "volume",
                    "t": "timestamp",
                    "s": "status",
                }
            )
            stock_candle_timeseries = df.set_index("timestamp")
            return stock_candle_timeseries

    def run(self):
        date_from = self.last_poll_datetime
        date_to = datetime.utcnow()

        ts = self.query_stock_candles(
            symbol="GME", date_from=date_from, date_to=date_to
        )
        if ts is not None:
            print("Sending financial data to Kafka queue...")
            self.producer.send(TOPIC_NAME, value=ts.to_json(orient="records"))
            self.producer.flush()
            print(f"stock price from {date_from} to {date_to} is send to Kafka")
        time.sleep(300)
        self.last_poll_datetime = date_to


if __name__ == "__main__":
    finnhub_service = finnhub_producer(api_token=AUTH_TOKEN)
    finnhub_service.run()
