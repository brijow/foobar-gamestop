import os

import foobar.preprocessing as pp
from foobar.data_loader import (
    get_or_create_processed_data_dir,
    load_reddit_comments_data_reader,
)

CHUNKSIZE = 1000000


def raw_comments_csv_to_post_records():
    reader = load_reddit_comments_data_reader(chunksize=CHUNKSIZE)
    batch_num = 0
    for df in reader:
        df = df.dropna()

        if df.empty:
            continue

        # Date cleaning
        df = pp.filter_bad_utcs(df, col="created_utc")
        df["created_dt"] = pp.utc_to_datetime(df, "created_utc")
        df = pp.filter_by_date(df, "2020-04")

        if df.empty:
            continue

        df = pp.clean_text_col(df, col="body")

        if df.empty:
            continue

        print(f"Doing sentiment analysis on comments, batch {batch_num}")
        df = pp.perform_sentiment_analysis(df, col="body")

        if df.empty:
            continue

        print(f"Doing tag extraction on comments, batch {batch_num}")
        tags_df = pp.perform_tag_extraction(df, col="body")

        df = pp.prep_comment_cols_for_db(df)
        df = pp.select_post_record_cols(df)

        print(f"Commiting comment posts to csvs, batch {batch_num}")
        save_comment_post_records(df, batch_num)

        print(f"Commiting comment tags to csvs, batch {batch_num}")
        save_tags_records(tags_df, batch_num)

        batch_num += 1


def save_tags_records(df, batch_num):
    if not df.empty:
        processed_data_dir = get_or_create_processed_data_dir()
        data_dir = os.path.join(processed_data_dir, "tags1")
        dir_path = os.path.expanduser(data_dir)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        filename = os.path.join(data_dir, "tags.csv")
        with open(filename, "a") as f:
            df.to_csv(f, header=f.tell() == 0, index=False)


def save_comment_post_records(df, batch_num):
    if not df.empty:
        processed_data_dir = get_or_create_processed_data_dir()
        data_dir = os.path.join(processed_data_dir, "posts1")
        dir_path = os.path.expanduser(data_dir)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        filename = os.path.join(data_dir, "posts.csv")
        with open(filename, "a") as f:
            df.to_csv(f, header=f.tell() == 0, index=False)


if __name__ == "__main__":
    raw_comments_csv_to_post_records()
