import configparser
import logging
from datetime import datetime, timedelta

import finnhub
import pandas as pd

# Finnhub API config
# config = configparser.ConfigParser()
# config.read("foobar_gamestop/finnhub/api.cfg")
# api_credential = config["api_credential"]
AUTH_TOKEN = os.environ.get("FINNHUB_AUTH_TOKEN")

# Coonfigure logger
logger = logging.getLogger("finnhub_dataset_get")
hdlr = logging.FileHandler("foobar_gamestop/finnhub/logs/data_get.log")
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.ERROR)


class finnhub_dataloader:
    def __init__(self, api_token):
        self.api_client = finnhub.Client(api_key=api_token)

    def query_stock_candles(self, symbol, resolution, date_from, date_to):
        # args:
        # symbol= (string) company stock symbol
        # resolution= (1 character) data resolution - Supported resolution includes 1, 5, 15, 30, 60, D, W, M
        # date_from= (datetime)
        # date_to= (datetime)

        from_ts = int(datetime.timestamp(date_from))
        to_ts = int(datetime.timestamp(date_to))

        df = pd.DataFrame(
            self.api_client.stock_candles(
                symbol=symbol, resolution=resolution, _from=from_ts, to=to_ts
            )
        )
        # print(df)
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


if __name__ == "__main__":
    # define datetime range for historical data (set to 3 years)
    date_to = datetime(year=2021, month=1, day=1)
    date_from = date_to - timedelta(days=3 * 365)
    # data resolution: options 1, 5, 15, 30, 60, D, W, M as character
    data_resolution = "D"

    dataloader = finnhub_dataloader(api_token=AUTH_TOKEN)

    stock_candle_timeseries = dataloader.query_stock_candles(
        symbol="GME", resolution=data_resolution, date_from=date_from, date_to=date_to
    )
    stock_candle_timeseries.to_csv(
        f"foobar_gamestop/datasets/samples/stock_candle_timeseries_{data_resolution}.csv",
        encoding="utf-8",
    )
    print("stock candle dataset is created.")

    sec_filling_sentiment_timeseries = dataloader.query_filling_sentiment(
        symbol="GME", date_from=date_from, date_to=date_to
    )
    sec_filling_sentiment_timeseries.to_csv(
        "foobar_gamestop/datasets/samples/filling_sentiment_ts.csv", encoding="utf-8",
    )
    print("SEC sentiment analysis dataset is created.")
