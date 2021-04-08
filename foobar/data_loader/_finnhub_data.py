import configparser
import os
from datetime import datetime, timedelta
import time

import finnhub
import pandas as pd

FINNHUB_FILE_PATH = "foobar/data/raw/"


# Finnhub API config
config = configparser.ConfigParser()
config.read("foobar/data_loader/conf/finnhub.cfg")
api_credential = config["api_credential"]
AUTH_TOKEN = api_credential["auth_token"]


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

        out = self.api_client.stock_candles(
            symbol=symbol, resolution=resolution, _from=from_ts, to=to_ts
        )
        if out["s"] == "no_data":
            return
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
                    print(
                        f"SEC filling report with access number {ac} does not have sentiment analysis. Error Msg: {e}"
                    )
                    pass

        df = pd.DataFrame(sentiments)
        ts = df.set_index("timestamp")
        return ts


def get_filling_sentiment(dataloader, date_from, date_to):
    from_str = date_from.strftime("%Y-%m-%d")
    to_str = date_to.strftime("%Y-%m-%d")
    if os.path.exists(FINNHUB_FILE_PATH + f"filling_sentiment_{from_str}_{to_str}.csv"):
        print("SEC sentiment analysis dataset is already created.")
    else:
        sec_filling_sentiment_timeseries = dataloader.query_filling_sentiment(
            symbol="GME", date_from=date_from, date_to=date_to
        )
        sec_filling_sentiment_timeseries.to_csv(
            FINNHUB_FILE_PATH + f"filling_sentiment_{from_str}_{to_str}.csv",
            encoding="utf-8",
        )
        print("SEC sentiment analysis dataset is successfully created.")


def get_stock_candle(dataloader, data_resolution, date_from, date_to):
    from_str = date_from.strftime("%Y-%m-%d")
    to_str = date_to.strftime("%Y-%m-%d")
    if os.path.exists(
        FINNHUB_FILE_PATH + f"stock_candle_{data_resolution}_{from_str}_{to_str}.csv"
    ):
        print("Stock candle dataset is already created.")
    else:
        f = date_from
        time_step = timedelta(days=5)
        t = f + time_step
        record_count = 0
        while t < date_to:
            stock_candle_timeseries = dataloader.query_stock_candles(
                symbol="GME", resolution=data_resolution, date_from=f, date_to=t,
            )
            time.sleep(2)
            if stock_candle_timeseries is not None:
                if os.path.exists(
                    FINNHUB_FILE_PATH
                    + f"stock_candle_{data_resolution}_{from_str}_{to_str}.csv"
                ):
                    stock_candle_timeseries.to_csv(
                        FINNHUB_FILE_PATH
                        + f"stock_candle_{data_resolution}_{from_str}_{to_str}.csv",
                        encoding="utf-8",
                        mode="a",
                        header=False,
                    )
                else:
                    stock_candle_timeseries.to_csv(
                        FINNHUB_FILE_PATH
                        + f"stock_candle_{data_resolution}_{from_str}_{to_str}.csv",
                        encoding="utf-8",
                        mode="a",
                        header=True,
                    )
                record_count += len(stock_candle_timeseries)
            f = t
            if t + time_step > date_to:
                t = date_to
            else:
                t += time_step
            print(t)
        # stock_candle_timeseries = dataloader.query_stock_candles(
        #         symbol="GME",
        #         resolution=data_resolution,
        #         date_from=date_from,
        #         date_to=date_to,
        #     )
        # record_count = len(stock_candle_timeseries)
        print(
            f"Stock candle dataset is successfully created. data size: {record_count}"
        )


if __name__ == "__main__":

    # Train datetime range, 3 years of historical data
    date_to = datetime(year=2021, month=1, day=1)
    date_from = datetime(year=2020, month=3, day=1)

    # Test datetime range: Short Squeeze period
    # date_to = datetime(year=2021, month=3, day=1)
    # date_from = datetime(year=2020, month=12, day=1)

    # data resolution: options 1, 5, 15, 30, 60, D, W, M as character
    data_resolution = "60"

    dataloader = finnhub_dataloader(api_token=AUTH_TOKEN)

    get_stock_candle(dataloader, data_resolution, date_from, date_to)

    get_filling_sentiment(dataloader, date_from, date_to)
