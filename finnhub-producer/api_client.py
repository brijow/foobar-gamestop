import configparser
import json
import os
import pandas as pd
from kafka import KafkaProducer
from datetime import datetime
import time
import finnhub

# from dataprep.connector import connect, info

# Finnhub API config
config = configparser.ConfigParser()
config.read("finnhub-producer/api.cfg")
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
    def __init__(self):
        # self.api_client = connect('finnhub', _auth={"access_token":AUTH_TOKEN})
        self.api_client = finnhub.Client(api_key=AUTH_TOKEN)
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER_URL,
            value_serializer=lambda x: json.dumps(x).encode("utf8"),
            api_version=(0, 11, 5),
        )
        # time.sleep(1)

    # async def query_short_interest(self, symbol, date_from, date_to):
    #     df = await self.api_client.query('short_interest',
    #                                     symbol=symbol,
    #                                     from_=date_from,
    #                                     to=date_to)
    #     return df

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

    def query_filling_sentiment(self, symbol, date_from, date_to):
        access_numbers_df = pd.DataFrame(
            self.api_client.filings(symbol=symbol, _from=date_from, to=date_to)
        )

        sentiments = []
        for i, row in access_numbers_df.iterrows():
            ac = row["accessNumber"]
            if len(ac) > 0:
                try:
                    dic = self.api_client.sec_sentiment_analysis(access_number=ac)
                    timestamp = int(
                        datetime.timestamp(
                            datetime.strptime(row["filedDate"], "%Y-%m-%d %H:%M:%S")
                        )
                    )
                    dic["timestamp"] = timestamp
                    sentiments.append(dic)
                except:
                    # print('error')
                    pass

        df = pd.DataFrame(sentiments)
        ts = df.set_index("timestamp")
        return ts

    def run(self):
        # self.producer.send(TOPIC_NAME, value=earning_df)
        ts = self.query_stock_candles(
            symbol="GME", date_from="2021-01-01", date_to="2021-03-01"
        )
        # print(ts)
        # ts.to_csv('stock_candle_timeseries.csv', encoding='utf-8')
        sentiment_ts = self.query_filling_sentiment(
            symbol="GME", date_from="2021-01-01", date_to="2021-03-01"
        )
        # print(sentiment_ts)
        # sentiment_ts.to_csv('filling_sentiment_ts.csv', encoding='utf-8')


if __name__ == "__main__":
    finnhub_service = finnhub_producer()
    finnhub_service.run()
