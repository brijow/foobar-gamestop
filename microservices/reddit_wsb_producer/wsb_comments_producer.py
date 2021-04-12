"""Produce openweathermap content to 'weather' kafka topic."""
import asyncio
import json
import os
import time
from collections import namedtuple
import uuid
import pandas as pd
import praw
from kafka import KafkaProducer

import foobar.preprocessing as pp


def comments_monitor(dummy):
    print("Starting comments monitor")
    KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
    POST_TOPIC_NAME = os.environ.get("POST_TOPIC_NAME")
    TAG_TOPIC_NAME = os.environ.get("TAG_TOPIC_NAME")
    BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 100))
    PRAW_CLIENT_ID = str(os.environ.get("PRAW_CLIENT_ID1"))
    PRAW_CLIENT_SECRET = str(os.environ.get("PRAW_CLIENT_SECRET1"))

    reddit = praw.Reddit(client_id=PRAW_CLIENT_ID,
    client_secret=PRAW_CLIENT_SECRET,
    user_agent="reddit wsb comments producer")

    if not reddit.read_only:
        print("Error connecting via reddit API!")
        return

    subreddit = reddit.subreddit("wallstreetbets")
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        # Encode all values as JSON
        value_serializer=lambda x: x.encode('utf8'),
    )
    for comment in subreddit.stream.comments(skip_existing=True):
        res = {}        
        for key, val in vars(comment).items():
            if key in [
                "author_fullname",
                "body",
                "created_utc",
                "id",
                "link_id",
                "parent_id",
                "score",
            ]:
                res[key] = [val]
            elif key == "author":
                res['author'] = [comment.author.name]

        df = pd.DataFrame(res)
        # df = pp.filter_by_date(df, "2020-04")
        df["dt"] = pd.to_datetime(df["created_utc"], unit="s")
        df = pp.clean_text_col(df, col="body")
        df = pp.perform_sentiment_analysis(df, col="body")

        if df.empty:
            print("Empty df")
            continue
        
        def get_tags_df():
            tags_df = pp.perform_entity_extraction(df, col="body")
            if tags_df.empty: return tags_df
            tags_df = pp.filter_tags_by_stock_tags(tags_df)
            if tags_df.empty: return tags_df
            return tags_df
        tags_ = get_tags_df()
        if not tags_.empty:
            print("Sending to tags topic")
            tags_['id'] = str(uuid.uuid4())
            for index, row in tags_.iterrows():
                print(row.to_json())
                producer.send(TAG_TOPIC_NAME, value=row.to_json())

        df = pp.prep_comment_cols_for_db(df)
        df = pp.select_post_record_cols(df)
        print("Sending new comment record")
        df['dt'] = df['dt'].dt.strftime("%Y-%m-%d %H:%M:%S")
        for index, row in df.iterrows():
            print(row.to_json())
            producer.send(POST_TOPIC_NAME, value=row.to_json())
        print("Comment record sent")

if __name__ == "__main__":
    comments_monitor('dummy')