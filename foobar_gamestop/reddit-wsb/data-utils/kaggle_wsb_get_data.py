import json
import os

import pandas as pd
import praw
import requests
from kaggle.api.kaggle_api_extended import KaggleApi

REDDIT_POSTS_FILE_PATH = '../data/raw/'
REDDIT_COMMENTS_PATH = '../data/raw/reddit_comments/'

# KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
# TOPIC_NAME = os.environ.get("TOPIC_NAME")
api = KaggleApi()

reddit = praw.Reddit('reddit_wsb', user_agent="reddit wsb producer")

comment_attributes = ['total_awards_received', 'link_id', 'id', 'author', 'parent_id',
                      'score', 'author_fullname', 'subreddit_id', 'body', 'created_utc']


def reddit_comments(post_id):
    if os.path.isfile(REDDIT_COMMENTS_PATH + post_id + ".csv"):
        return True
    submission = reddit.submission(id=post_id)
    try:
        submission.comments.replace_more()  # Default limit = 32, default threshold = 0
        comments = pd.DataFrame.from_records(
            [c.__dict__ for c in submission.comments.list()])
    except:
        print("Excepting ", post_id)
        json = requests.get(f"https://api.pushshift.io/reddit/comment/search?link_id={post_id}&limit=2000&sort=desc", headers={
                            'User-Agent': "reddit wsb producer"})
        comments = pd.DataFrame.from_records(
            [comment for comment in json.json()['data']])
    try:
        comments.to_csv(REDDIT_COMMENTS_PATH + post_id + ".csv",
                        columns=comment_attributes, index_label='id')
    except KeyError:
        comments.to_csv(REDDIT_COMMENTS_PATH + post_id + ".csv", index_label='id')
    print("Done ", post_id)


def get_posts():
    api.authenticate()
    api.dataset_download_files(
        'gpreda/reddit-wallstreetsbets-posts', path=REDDIT_POSTS_FILE_PATH, unzip=True)
    if os.path.isfile(REDDIT_POSTS_FILE_PATH + "reddit_wsb.csv"):
        return True
    return False


def get_comments():
    if not reddit.read_only:
        print("Error connecting via reddit API!")
        return
    posts = pd.read_csv(REDDIT_POSTS_FILE_PATH + "reddit_wsb.csv")
    posts['comments'] = posts['id'].apply(reddit_comments)


if __name__ == "__main__":
    if get_posts():
        get_comments()
    else:
        print("Kaggle dataset download failed")
