import configparser
import os
import time
from datetime import datetime, timedelta

import finnhub
import pandas as pd
from _base import get_data_loader_conf_dir, get_or_create_raw_data_dir

# Finnhub API config
config = configparser.ConfigParser()
config.read(os.path.join(get_data_loader_conf_dir(), "finnhub.cfg"))
api_credential = config["api_credential"]
AUTH_TOKEN = api_credential["auth_token"]


class finnhub_dataloader:
    def __init__(self, api_token):
        self.api_client = finnhub.Client(api_key=api_token)

    def get_stock_candle(self, data_resolution, date_from, date_to):
        from_str = date_from.strftime("%Y-%m-%d")
        to_str = date_to.strftime("%Y-%m-%d")
        stock_candle_file = os.path.join(
            get_or_create_raw_data_dir(),
            f"stock_candle_{data_resolution}_{from_str}_{to_str}.csv",
        )
        if os.path.exists(stock_candle_file):
            print("Stock candle dataset is already created.")
        else:
            f = date_from
            time_step = timedelta(days=5)
            t = f + time_step
            record_count = 0
            while t < date_to:
                out = self.api_client.stock_candles(
                    symbol="GME",
                    resolution=data_resolution,
                    _from=int(datetime.timestamp(f)),
                    to=int(datetime.timestamp(t)),
                )
                time.sleep(2)
                if out["s"] == "no_data":
                    print("no data")
                    pass
                else:
                    stock_candle_timeseries = pd.DataFrame(out)
                    stock_candle_timeseries = stock_candle_timeseries.rename(
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
                    if os.path.exists(stock_candle_file):
                        stock_candle_timeseries.to_csv(
                            stock_candle_file,
                            encoding="utf-8",
                            mode="a",
                            header=False,
                        )
                    else:
                        stock_candle_timeseries.to_csv(
                            stock_candle_file,
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
            print(
                f"Stock candle dataset is successfully created. data size: {record_count}"
            )


if __name__ == "__main__":
    # data resolution: options 1, 5, 15, 30, 60, D, W, M as character
    # 60  = hourly data resolution
    data_resolution = "60"

    # datatime range of the Gamestop Shortsqueeze, March 1, 2020 to March 1, 2021
    train_from = datetime(year=2020, month=3, day=1)
    train_to = datetime(year=2021, month=3, day=1)

    # instantiate finnhub dataloader object with the api token
    dataloader = finnhub_dataloader(api_token=AUTH_TOKEN)
    dataloader.get_stock_candle(data_resolution, train_from, train_to)
