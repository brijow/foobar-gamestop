import os

import foobar.preprocessing as pp
from foobar.data_loader import (
    get_or_create_processed_data_dir,
    load_reddit_submissions_data,
)


def raw_submissions_csv_to_post_records():
    df = load_reddit_submissions_data()

    df = pp.filter_by_cols(
        df,
        [
            "id",
            "title",
            "score",
            "author",
            "created_utc",
        ],
    )
    df = pp.filter_by_date(df, "2020-04")
    df = pp.clean_text_col(df, col="title")
    df = pp.perform_sentiment_analysis(df, col="title")

    tags_df = pp.perform_entity_extraction(df, col="title")
    tags_df = pp.filter_tags_by_stock_tags(tags_df)

    df = pp.prep_submission_cols_for_db(df)
    df = pp.select_post_record_cols(df)

    save_submission_post_records(df)
    save_tags_records(tags_df)


def save_tags_records(df):
    if not df.empty:
        processed_data_dir = get_or_create_processed_data_dir()
        data_dir = os.path.join(processed_data_dir, "tags")
        dir_path = os.path.expanduser(data_dir)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        filename = os.path.join(data_dir, "subs_tags.csv")
        df.to_csv(filename)


def save_submission_post_records(df):
    if not df.empty:
        processed_data_dir = get_or_create_processed_data_dir()
        data_dir = os.path.join(processed_data_dir, "posts")
        dir_path = os.path.expanduser(data_dir)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        filename = os.path.join(data_dir, "subs_posts.csv")
        df.to_csv(filename)


if __name__ == "__main__":
    raw_submissions_csv_to_post_records()
