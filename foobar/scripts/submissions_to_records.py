import os

import foobar.preprocessing as pp
from foobar.data_loader import (
    get_or_create_processed_data_dir,
    load_reddit_submissions_data,
)


def raw_submissions_csv_to_post_records():
    df = load_reddit_submissions_data()

    df = df.dropna()

    # Date cleaning
    df = pp.filter_bad_utcs(df, col="created_utc")
    df["created_dt"] = pp.utc_to_datetime(df, "created_utc")
    df = pp.filter_by_date(df, "2020-04")

    df = pp.clean_text_col(df, col="title")

    print("Doing sentiment analysis on submissions")
    df = pp.perform_sentiment_analysis(df, col="title")

    print("Doing tag extraction on submissions")
    tags_df = pp.perform_tag_extraction(df, col="title")

    df = pp.prep_submission_cols_for_db(df)
    df = pp.select_post_record_cols(df)

    print("Commiting submissions posts to csvs")
    save_submission_post_records(df)

    print("Commiting submissions tags to csvs")
    save_tags_records(tags_df)


def save_tags_records(df):
    if not df.empty:
        processed_data_dir = get_or_create_processed_data_dir()
        data_dir = os.path.join(processed_data_dir, "tags")
        dir_path = os.path.expanduser(data_dir)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        filename = os.path.join(data_dir, "tags.csv")
        with open(filename, "a") as f:
            df.to_csv(f, header=f.tell() == 0, index=False)


def save_submission_post_records(df):
    if not df.empty:
        processed_data_dir = get_or_create_processed_data_dir()
        data_dir = os.path.join(processed_data_dir, "posts")
        dir_path = os.path.expanduser(data_dir)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        filename = os.path.join(data_dir, "posts.csv")
        with open(filename, "a") as f:
            df.to_csv(f, header=f.tell() == 0, index=False)


if __name__ == "__main__":
    raw_submissions_csv_to_post_records()
