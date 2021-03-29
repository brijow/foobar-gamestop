from foobar_gamestop.datasets import load_kaggle_data

DATASET = "gpreda/reddit-wallstreetsbets-posts"
LOCAL_FILE_NAME = "reddit_wsb.csv"


def load_reddit_data(download_if_missing=True):
    """Load reddit dataset from kaggle."""
    reddit_df = load_kaggle_data(
        local_fname=LOCAL_FILE_NAME,
        dataset=DATASET,
        unzip=True,
        download_if_missing=download_if_missing,
    )
    return reddit_df
