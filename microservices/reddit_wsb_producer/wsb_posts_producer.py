"""Produce openweathermap content to 'weather' kafka topic."""
import asyncio
import os
import time
from collections import namedtuple

import praw

# from kafka import KafkaProducer


# KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
# TOPIC_NAME = os.environ.get("TOPIC_NAME")
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 100))

reddit = praw.Reddit("reddit_wsb", user_agent="reddit wsb producer")

# access_token = api_credential['access_token']
# reddit = praw.Reddit(
#     client_id="my client id",
#     client_secret="my client secret",
#     user_agent="my user agent",
# )
# ApiInfo = namedtuple('ApiInfo', ['name', 'access_token'])
# apiInfo = ApiInfo('openweathermap', access_token)

# sc = connect(apiInfo.name,
#              _auth={'access_token': apiInfo.access_token},
#              _concurrency=3)


def run():
    # kafkaurl = KAFKA_BROKER_URL
    subreddit = reddit.subreddit("wallstreetbets")
    for submission in subreddit.stream.submissions(skip_existing=True):
        print(submission)
        print(type(submission))
        print(vars(submission))
    # for comment in subreddit.stream.comments(skip_existing=True):
    #     print(comment)


if __name__ == "__main__":
    if reddit.read_only:
        run()
    else:
        print("Error connecting via reddit API!")
