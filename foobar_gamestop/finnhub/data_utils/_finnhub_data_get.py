import configparser
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import time
import finnhub
import logging

# Finnhub API config
config = configparser.ConfigParser()
config.read("foobar_gamestop/finnhub/api.cfg")
api_credential = config["api_credential"]
AUTH_TOKEN = api_credential["auth_token"]

# Coonfigure logger
logger = logging.getLogger("finnhub_dataset_get")
hdlr = logging.FileHandler("foobar_gamestop/finnhub/logs/data_get.log")
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.ERROR)


class finnhub_producer:
    def __init__(self):
        self.api_client = finnhub.Client(api_key=AUTH_TOKEN)

    def query_stock_candles(self, symbol, date_from, date_to):
        from_ts = int(datetime.timestamp(date_from))
        to_ts = int(datetime.timestamp(date_to))

        # data resolution is set to 5 minutes
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
                except Exception as e:
                    logger.error(
                        "SEC filling report with access number {0} does not have sentiment analysis. Error Msg: {1}".format(
                            ac, e
                        )
                    )
                    pass

        df = pd.DataFrame(sentiments)
        ts = df.set_index("timestamp")
        return ts

    def run(self):
        date_from = datetime.utcnow() - timedelta(days=3 * 365)
        date_to = datetime.utcnow()

        ts = self.query_stock_candles(
            symbol="GME", date_from=date_from, date_to=date_to
        )
        # print(ts)
        ts.to_csv(
            "foobar_gamestop/datasets/samples/stock_candle_timeseries.csv",
            encoding="utf-8",
        )
        sentiment_ts = self.query_filling_sentiment(
            symbol="GME", date_from=date_from, date_to=date_to
        )
        # print(sentiment_ts)
        sentiment_ts.to_csv(
            "foobar_gamestop/datasets/samples/filling_sentiment_ts.csv",
            encoding="utf-8",
        )


if __name__ == "__main__":
    finnhub_service = finnhub_producer()
    finnhub_service.run()
