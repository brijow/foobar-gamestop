from cassandra.cluster import Cluster
from cassandra.query import dict_factory
from cassandra.auth import PlainTextAuthProvider
from datetime import datetime, timedelta
import os
import pandas as pd

from foobar.db_utils.queries import (
    select_posts_by_hour_range,
    select_tags_by_postids,
    select_all_from_wide_table,
    select_gamestops_by_hour_range,
)

CASSANDRA_HOST = (
    os.environ.get("CASSANDRA_HOST")
    if os.environ.get("CASSANDRA_HOST")
    else "localhost"
)
CASSANDRA_KEYSPACE = (
    os.environ.get("CASSANDRA_KEYSPACE")
    if os.environ.get("CASSANDRA_KEYSPACE")
    else "kafkapipeline"
)
CASSANDRA_USER = os.environ.get("CASSANDRA_USER")
CASSANDRA_PWD = os.environ.get("CASSANDRA_PWD")

WIDE_COLS = [
    "hour",
    "avg_all_post_pos",
    "avg_all_post_neg",
    "avg_all_post_neu",
    "cnt_all_user",
    "cnt_all_tag",
    "cnt_all_post",
    "cnt_all_comments",
    "avg_gme_post_pos",
    "avg_gme_post_neg",
    "avg_gme_post_neu",
    "cnt_gme_user",
    "cnt_gme_tag",
    "cnt_gme_post",
    "cnt_gme_comments",
    "open_price",
    "low_price",
    "high_price",
    "volume",
    "close_price",
    "prediction_finn",
    "prediction_wide",
    "prediction_reddit",
]

WIDE_REDDIT_COLS = [
    "hour",
    "avg_all_post_pos",
    "avg_all_post_neg",
    "avg_all_post_neu",
    "cnt_all_user",
    "cnt_all_tag",
    "cnt_all_post",
    "cnt_all_comments",
    "avg_gme_post_pos",
    "avg_gme_post_neg",
    "avg_gme_post_neu",
    "cnt_gme_user",
    "cnt_gme_tag",
    "cnt_gme_post",
    "cnt_gme_comments",
]

GAMESTOP_COLS = [
    "hour",
    "open_price",
    "low_price",
    "high_price",
    "volume",
    "close_price",
    "prediction_finn",
]

POST_COLS = [
    "hour",
    "id",
    "iscomment",
    "negative",
    "neutral",
    "parent_id",
    "positive",
    "submission_id",
    "username",
]

TAG_COLS = ["post_id", "id", "tag_token"]


def build_wide_reddit_row(session, start_date, end_date, all_posts):
    """NOTE: only works on a hourly basis"""
    reddit_df = pd.DataFrame(columns=WIDE_REDDIT_COLS)
    posts_df = pd.DataFrame(columns=POST_COLS)
    tags_df = pd.DataFrame(columns=TAG_COLS)
    if all_posts.empty:
        print(
            (
                f"No posts found for date range {start_date} = {end_date}.\n"
                "Using last available row of reddit data from wide table."
            )
        )
        return reddit_df
    rowposts = all_posts[(all_posts['hour'] > start_date) & (all_posts['hour'] < end_date)]
    if not rowposts.empty:
        posts_df = posts_df.append(
            rowposts
        )
        tags_df = tags_df.append(select_tags_by_postids(session, posts_df["id"].tolist()))

    if posts_df.empty:
        print(
            (
                f"No posts found for date range {start_date} = {end_date}.\n"
                "Using last available row of reddit data from wide table."
            )
        )
        return reddit_df

    if tags_df.empty:
        print(
            (
                f"No tags found for posts in date range {start_date} = {end_date}.\n"
                "Still performing reddit join logic but no new tag info will be present."
            )
        )

    reddit_row = dict()

    df = posts_df.set_index("id").join(tags_df.set_index("post_id"))

    all_sentiments = df[["positive", "negative", "neutral"]].mean().fillna(0)

    all_sentiments = all_sentiments.rename(
        {
            "positive": "avg_all_post_pos",
            "negative": "avg_all_post_neg",
            "neutral": "avg_all_post_neu",
        }
    )

    gme_df = df[df["tag_token"] == "GME"]

    gme_sentiments = gme_df[["positive", "negative", "neutral"]].mean().fillna(0)
    gme_sentiments = gme_sentiments.rename(
        {
            "positive": "avg_gme_post_pos",
            "negative": "avg_gme_post_neg",
            "neutral": "avg_gme_post_neu",
        }
    )

    reddit_row["cnt_all_comments"] = len(df[df["iscomment"] == True])
    reddit_row["cnt_all_post"] = len(df[df["iscomment"] == False])
    reddit_row["cnt_all_tag"] = len(df)
    reddit_row["cnt_all_user"] = df["username"].nunique()
    reddit_row["avg_all_post_neg"] = all_sentiments["avg_all_post_neg"]
    reddit_row["avg_all_post_neu"] = all_sentiments["avg_all_post_neu"]
    reddit_row["avg_all_post_pos"] = all_sentiments["avg_all_post_pos"]
    reddit_row["cnt_gme_comments"] = len(gme_df[gme_df["iscomment"] == True])
    reddit_row["cnt_gme_post"] = len(gme_df[gme_df["iscomment"] == False])
    reddit_row["cnt_gme_tag"] = len(gme_df)
    reddit_row["cnt_gme_user"] = gme_df["username"].nunique()
    reddit_row["avg_gme_post_neg"] = gme_sentiments["avg_gme_post_neg"]
    reddit_row["avg_gme_post_neu"] = gme_sentiments["avg_gme_post_neu"]
    reddit_row["avg_gme_post_pos"] = gme_sentiments["avg_gme_post_pos"]
    reddit_row["hour"] = start_date

    reddit_df = reddit_df.append(reddit_row, ignore_index=True)
    return reddit_df


def new_cassandra_session(auth=True):
    auth_provider = (
        PlainTextAuthProvider(username=CASSANDRA_USER, password=CASSANDRA_PWD)
        if auth
        else None
    )
    cluster = Cluster([CASSANDRA_HOST], auth_provider=auth_provider)

    session = cluster.connect(CASSANDRA_KEYSPACE)
    session.row_factory = dict_factory
    return session



def run_wide_row_builder(data_point_time_step="H"):
    session = new_cassandra_session()
    wide_df = select_all_from_wide_table(session)
    # wide_df = pd.read_csv("wide.csv")
    wide_df["hour"] = pd.to_datetime(wide_df["hour"])
    last_time = wide_df["hour"].max()
    curr_time = datetime.now()
    time_range = pd.date_range(last_time, curr_time, freq="H")

    if len(time_range) <= 1:
        print("nothing to update in wide table")
        return

    reddit_df = pd.DataFrame(columns=WIDE_REDDIT_COLS)
    gamestop_df = pd.DataFrame(columns=GAMESTOP_COLS)

    all_posts = select_posts_by_hour_range(session, last_time, curr_time)

    time_df = pd.DataFrame({"h0": time_range, "h1": time_range + timedelta(hours=1)})
    for _, row in time_df.iterrows():
        start_date, end_date = row["h0"], row["h1"]

        reddit_single_hour_df = build_wide_reddit_row(session, start_date, end_date, all_posts)

        if reddit_single_hour_df.empty:
            reddit_single_hour_df = wide_df.iloc[-1][WIDE_REDDIT_COLS]
            reddit_single_hour_df["hour"] = start_date

        reddit_df = reddit_df.append(reddit_single_hour_df)

    reddit_df.reset_index(drop=True, inplace=True)

    gamestop_df = gamestop_df.append(
        select_gamestops_by_hour_range(session, last_time, curr_time)
    )

    time_joiner = time_df.set_index("h0")
    gamestop_df = time_joiner.join(gamestop_df[GAMESTOP_COLS].set_index("hour"))
    gamestop_df = gamestop_df.rename(columns={"h1": "hour"}).reset_index(drop=True)
    last_gme_row = wide_df.iloc[-1][GAMESTOP_COLS]
    gamestop_df = (
        gamestop_df.append(last_gme_row).sort_values(by="hour").reset_index(drop=True)
    )
    gamestop_df = gamestop_df.ffill()

    result = pd.merge(reddit_df, gamestop_df, on='hour')
    newrows = pd.merge(result, wide_df['hour'], on='hour', how="outer", indicator=True)
    newrows = newrows[newrows['_merge'] == 'left_only']
    result = pd.concat([wide_df, newrows], axis=0)
    result = result.fillna(-1)
    result = result.reset_index()
    
    return result[WIDE_COLS]
