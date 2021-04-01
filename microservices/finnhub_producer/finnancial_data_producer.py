import configparser
import json
import os
import pandas as pd
from kafka import KafkaProducer
from datetime import datetime
import time
import finnhub

# Finnhub API config
config = configparser.ConfigParser()
config.read("foobar_gamestop/finnhub/api.cfg")
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

    _last_poll_datetime = datetime.utcnow()

    def __init__(self):

        self.api_client = finnhub.Client(api_key=AUTH_TOKEN)
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER_URL,
            value_serializer=lambda x: json.dumps(x).encode("utf8"),
            api_version=(0, 11, 5),
        )

    def query_stock_candles(self, symbol, date_from, date_to):
        from_ts = int(datetime.timestamp(datetime.strptime(date_from, "%Y-%m-%d")))
        to_ts = int(datetime.timestamp(datetime.strptime(date_to, "%Y-%m-%d")))
        df = pd.DataFrame(
            self.api_client.stock_candles(
                symbol=symbol, resolution="5", _from=from_ts, to=to_ts
            )
        )
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
        date_from = _last_poll_datetime
        date_to = datetime.utcnow()
        ts = self.query_stock_candles(
            symbol="GME", date_from=date_from, date_to=date_to
        )
        self.producer.send(TOPIC_NAME, value=earning_df)
        time.sleep(300)


if __name__ == "__main__":
    finnhub_service = finnhub_producer()
    finnhub_service.run()
