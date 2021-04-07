import os

import foobar.preprocessing as pp
from foobar.data_loader import (
    get_or_create_processed_data_dir,
    load_reddit_comments_data_reader,
)

CHUNKSIZE = 50000


def raw_comments_csv_to_post_records():
    reader = load_reddit_comments_data_reader(chunksize=CHUNKSIZE)
    batch_num = 0
    for df in reader:

        df = pp.filter_by_cols(
            df,
            [
                "author",
                "author_fullname",
                "body",
                "created_utc",
                "id",
                "link_id",
                "parent_id",
                "score",
            ],
        )
        df = pp.filter_by_date(df, "2020-04")
        df = pp.clean_text_col(df, col="body")
        df = pp.perform_sentiment_analysis(df, col="body")

        tags_df = pp.perform_entity_extraction(df, col="body")

        df = pp.prep_comment_cols_for_db(df)
        df = pp.select_post_record_cols(df)

        save_comment_post_records(df, batch_num)
        save_tags_records(tags_df, batch_num)
        batch_num += 1


def save_tags_records(df, batch_num):
    if not df.empty:
        processed_data_dir = get_or_create_processed_data_dir()
        filename = os.path.join(
            processed_data_dir, "tags", "tagss_batch_" + str(batch_num)
        )
        df.to_csv(filename)


def save_comment_post_records(df, batch_num):
    if not df.empty:
        processed_data_dir = get_or_create_processed_data_dir()
        filename = os.path.join(
            processed_data_dir, "posts", "posts_batch_" + str(batch_num)
        )
        df.to_csv(filename)


if __name__ == "__main__":
    raw_comments_csv_to_post_records()
