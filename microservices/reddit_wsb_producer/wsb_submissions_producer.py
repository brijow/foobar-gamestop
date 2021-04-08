import asyncio
import json
import os
import time
from collections import namedtuple

import pandas as pd
import praw
from kafka import KafkaProducer

import foobar.preprocessing as pp


def submissions_monitor(dummy):
    print("Starting submissions monitor")
    KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
    POST_TOPIC_NAME = os.environ.get("POST_TOPIC_NAME")
    TAG_TOPIC_NAME = os.environ.get("TAG_TOPIC_NAME")
    BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 100))
    PRAW_CLIENT_ID = str(os.environ.get("PRAW_CLIENT_ID2"))
    PRAW_CLIENT_SECRET = str(os.environ.get("PRAW_CLIENT_SECRET2"))

    reddit = praw.Reddit(client_id=PRAW_CLIENT_ID,
    client_secret=PRAW_CLIENT_SECRET,
    user_agent="reddit wsb submissions producer")

    if not reddit.read_only:
        print("Error connecting via reddit API!")
        return

    subreddit = reddit.subreddit("wallstreetbets")
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        # Encode all values as JSON
        value_serializer=lambda x: x.encode('ascii'),
    )
    for submission in subreddit.stream.submissions(skip_existing=True):
        res = {}
        for key, val in vars(submission).items():
            if key in [
                "id",
                "title",
                "score",
                "body",
                "created_utc",
            ]:
                res[key] = [val]
            elif key == "author":
                res['author'] = [submission.author.name]
        df = pd.DataFrame(res)
        df = pp.filter_by_date(df, "2020-04")
        df = pp.clean_text_col(df, col="title")
        df = pp.perform_sentiment_analysis(df, col="title")

        tags_df = pp.perform_entity_extraction(df, col="title")
        tags_df = pp.filter_tags_by_stock_tags(tags_df)

        df = pp.prep_submission_cols_for_db(df)
        df = pp.select_post_record_cols(df)

        producer.send(POST_TOPIC_NAME, value=df.to_json(orient="records")[0])
        producer.send(TAG_TOPIC_NAME, value=tags_df.to_json(orient="records")[0])
        
if __name__ == "__main__":
    submissions_monitor('dummy')