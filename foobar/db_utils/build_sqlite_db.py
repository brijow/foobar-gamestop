import os

import pandas as pd
from sqlalchemy import create_engine

from foobar.data_loader import (
    get_or_create_processed_data_dir,
    get_or_create_raw_data_dir,
    get_root_data_dir,
    load_stock_ticker_tags,
)
from foobar.db_utils.models import Base, Gamestop, Post, Tag

data_dir = get_root_data_dir()


def _get_or_create_db_dir():
    """Return the path of the db dir."""
    db_dir = os.environ.get(
        "FOOBAR_SQLITE_DIR", os.path.join(get_root_data_dir(), "db")
    )
    dir_path = os.path.expanduser(db_dir)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


def create_gamestop_db(force_refresh=False):
    db_dir = _get_or_create_db_dir()
    file_path = os.path.join(db_dir, "gamestop.db")

    if os.path.exists(file_path) and force_refresh:
        os.remove(file_path)

    # if not os.path.exists(file_path):
    engine = create_engine(f"sqlite:///{file_path}")
    Base.metadata.create_all(engine)


def populate_posts_gamestop_db():

    db_dir = _get_or_create_db_dir()
    file_path = os.path.join(db_dir, "gamestop.db")
    engine = create_engine(f"sqlite:///{file_path}")

    proc_dir = get_or_create_processed_data_dir()
    post_dir = os.path.join(proc_dir, "posts")

    to_insert = pd.read_csv(post_dir + "/posts.csv")

    to_insert["dt"] = pd.to_datetime(to_insert["dt"])

    to_insert = to_insert.drop_duplicates()

    to_insert["submission_id"] = to_insert["submission_id"].str.replace(
        r"^t\d+_", "", regex=True
    )
    to_insert["parent_id"] = to_insert["parent_id"].str.replace(
        r"^t\d+_", "", regex=True
    )

    subs_with_cmts_or_cmts_with_subs = to_insert[to_insert["iscomment"] == 0].join(
        to_insert[to_insert["iscomment"] == 1].set_index("submission_id"),
        on="id",
        lsuffix="subs",
        how="inner",
    )[["idsubs", "id"]]

    posts_ids_to_keep = pd.concat(
        [subs_with_cmts_or_cmts_with_subs.idsubs, subs_with_cmts_or_cmts_with_subs.id]
    ).drop_duplicates()

    to_insert = to_insert[to_insert["id"].isin(posts_ids_to_keep)]

    # subids = to_insert.loc[to_insert["iscomment"] == 0, "id"]
    # cmtids = to_insert.loc[to_insert["iscomment"] == 1, "id"]

    try:
        engine.execute(Post.__table__.insert(), to_insert.to_dict("records"))
        print("Successful insert!")
        to_insert.to_csv(post_dir + "/posts_clean.csv")
        print("Successful csv save of posts_clean.csv!")
    except Exception as e:
        print("Initial failure to append: {}\n".format(e))


def populate_tags_gamestop_db():

    db_dir = _get_or_create_db_dir()
    file_path = os.path.join(db_dir, "gamestop.db")
    engine = create_engine(f"sqlite:///{file_path}")

    proc_dir = get_or_create_processed_data_dir()
    tag_dir = os.path.join(proc_dir, "tags")

    to_insert = pd.read_csv(tag_dir + "/tags.csv")
    to_insert = to_insert.rename(columns={"id": "post_id"})
    to_insert = to_insert.drop_duplicates()
    tickers = load_stock_ticker_tags()
    to_insert = to_insert[to_insert["tag"].isin(tickers["tickers"])].drop_duplicates()

    post_dir = os.path.join(proc_dir, "posts")
    post_ids = pd.read_csv(post_dir + "/posts_clean.csv", usecols=["id"])
    to_insert = to_insert[to_insert["post_id"].isin(post_ids["id"])]

    try:
        engine.execute(Tag.__table__.insert(), to_insert.to_dict("records"))
        print("Successful insert!")
        to_insert.to_csv(tag_dir + "/tags_clean.csv")
        print("Successful csv save of tags_clean.csv!")
    except Exception as e:
        print("Initial failure to append: {}\n".format(e))

    # Helpful try-except left here just for an FYI
    # try:
    #     to_insert.to_sql(name="post", con=engine, if_exists="append", index=False)
    #     print("Successful insert!")
    # except Exception as e:
    #     print("Initial failure to append: {}\n".format(e))
    #     print("Attempting to rectify...")
    #     existing = pd.read_sql("post", con=engine)
    #     mask = ~to_insert.id.isin(existing.id)
    # try:
    #     to_insert.loc[mask].to_sql(
    #         name="post", con=engine, if_exists="append", index=False
    #     )
    #     print("Successful deduplication.")
    # except Exception as e2:
    #     "Could not rectify duplicate entries. \n{}".format(e2)
    # print("Success after dedupe")


def populate_gamestop_gamestop_db():

    db_dir = _get_or_create_db_dir()
    file_path = os.path.join(db_dir, "gamestop.db")
    engine = create_engine(f"sqlite:///{file_path}")

    raw_dir = get_or_create_raw_data_dir()

    to_insert = pd.read_csv(raw_dir + "/stock_candle_60_2020-03-01_2021-03-01.csv")
    to_insert = to_insert.drop("Unnamed: 0", axis=1)
    to_insert["hour"] = pd.to_datetime(to_insert["timestamp"], unit="s")
    to_insert["prediction"] = -1.0
    to_insert = to_insert.rename(
        columns={
            "close_price": "closeprice",
            "high-price": "highprice",
            "low-price": "lowprice",
            "open_price": "openprice",
        }
    )
    to_insert = to_insert[
        [
            "openprice",
            "lowprice",
            "highprice",
            "closeprice",
            "volume",
            "hour",
            "prediction",
        ]
    ]
    to_insert = to_insert.drop_duplicates()

    try:
        engine.execute(Gamestop.__table__.insert(), to_insert.to_dict("records"))
        print("Successful insert!")
    except Exception as e:
        print("Initial failure to append: {}\n".format(e))
