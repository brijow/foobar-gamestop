import os

import foobar.preprocessing as pp
from foobar.data_loader import (
    get_or_create_processed_data_dir,
    load_reddit_submissions_data,
)


def raw_submissoins_csv_to_post_records():
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

    df = pp.prep_submission_cols_for_db(df)
    df = pp.select_post_record_cols(df)

    save_submission_post_records(df)
    save_tags_records(tags_df)


def save_tags_records(df):
    if not df.empty:
        processed_data_dir = get_or_create_processed_data_dir()
        filename = os.path.join(processed_data_dir, "tags", "subs_tags")
        df.to_csv(filename)


def save_submission_post_records(df):
    if not df.empty:
        processed_data_dir = get_or_create_processed_data_dir()
        filename = os.path.join(processed_data_dir, "posts", "subs_posts")
        df.to_csv(filename)


if __name__ == "__main__":
    raw_submissoins_csv_to_post_records()
