from ._base import load_kaggle_data

# SUBMISSIONS_DATASET = "gpreda/reddit-wallstreetsbets-posts"
# LOCAL_SUBMISSIONS_FILE_NAME = "reddit_wsb.csv"
SUBMISSIONS_DATASET = "unanimad/reddit-rwallstreetbets"
LOCAL_SUBMISSIONS_FILE_NAME = "r_wallstreetbets_posts.csv"

COMMENTS_DATASET = "mattpodolak/reddit-wallstreetbets-comments"
LOCAL_COMMENTS_FILE_NAME = "wsb_comments_raw.csv"


def load_reddit_submissions_data(download_if_missing=True):
    """Load reddit submissions dataset from kaggle."""
    submissions_df = load_kaggle_data(
        local_fname=LOCAL_SUBMISSIONS_FILE_NAME,
        dataset=SUBMISSIONS_DATASET,
        unzip=True,
        download_if_missing=download_if_missing,
    )
    return submissions_df


def load_reddit_comments_data_reader(download_if_missing=True, chunksize=50000):
    """Load reddit comments dataset from kaggle, (in a batch)."""
    comments_reader = load_kaggle_data(
        local_fname=LOCAL_COMMENTS_FILE_NAME,
        dataset=COMMENTS_DATASET,
        unzip=True,
        download_if_missing=download_if_missing,
        chunksize=chunksize,
    )
    return comments_reader
