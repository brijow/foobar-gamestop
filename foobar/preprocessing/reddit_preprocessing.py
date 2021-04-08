import re

import pandas as pd
import spacy as sp
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

from foobar.data_loader import load_all_stock_tags


def clean_text_col(df, col):
    def text_processing(text):
        text = str(text)  # remove handlers
        text = re.sub(r"@[^\s]+", "", text)
        text = re.sub(r"http\S+", "", text)  # remove URLS
        text = " ".join(re.findall(r"\w+", text))  # remove special chars
        text = re.sub(r"\s+[a-zA-Z]\s+", "", text)  # remove single chars
        text = re.sub(r"\s+", " ", text, flags=re.I)  # multiple to single spaces
        return text

    df[col] = df[col].apply(text_processing)
    df = df.dropna(subset=[col])
    return df


def perform_entity_extraction(df, col):
    nlps = sp.load("en_core_web_sm")

    def entity_extraction(x):
        _id, text = x["id"], x[col]
        doc = nlps(text)
        return [(_id, chunk.text) for chunk in doc.noun_chunks]

    tags_sf = df[["id", col]].apply(entity_extraction, axis=1)
    tags_sf = tags_sf.loc[tags_sf.astype(str) != "[]"]
    tags_df = pd.DataFrame(tags_sf.explode().tolist(), columns=["post_id", "tag"])

    tags_df["tag"] = tags_df["tag"].str.split()
    tags_df = tags_df.explode("tag")
    return tags_df


def filter_tags_by_stock_tags(tags_df):
    tags_df["tag"] = tags_df["tag"].str.upper()
    stock_tags_df = load_all_stock_tags()
    tags_df.loc[tags_df["tag"].isin(stock_tags_df["0"])]
    return tags_df


def filter_by_cols(df, cols_list):
    """Keep only columns in cols_list

    Note: potential comment columns include the following:

        "associated_award",
        "author",
        "author_flair_background_color",
        "author_flair_css_class",
        "author_flair_richtext",
        "author_flair_template_id",
        "author_flair_text",
        "author_flair_text_color",
        "author_flair_type",
        "author_fullname",
        "author_patreon_flair",
        "author_premium",
        "awarders",
        "body",
        "collapsed_because_crowd_control",
        "created_utc",
        "gildings",
        "id",
        "is_submitter",
        "link_id",
        "locked",
        "no_follow",
        "parent_id",
        "permalink",
        "retrieved_on",
        "score",
        "send_replies",
        "stickied",
        "subreddit",
        "subreddit_id",
        "total_awards_received",
        "treatment_tags",
        "top_awarded_type",
        "edited",
        "distinguished",
        "comment_type",
        "author_cakeday",
        "editable",
        "media_metadata",
    """
    cols_to_keep = [col for col in cols_list if col in df.columns]
    return df[cols_to_keep]


def filter_by_date(df, date_str):
    """Filter rows older than date_str

    Note: Using 2020-04-01 as min date results in 777164 records
    """
    df = df[df["created_utc"].apply(lambda x: str(x).isdigit())]
    df["created_dt"] = pd.to_datetime(df.created_utc, unit="s")
    return df[df["created_dt"] >= date_str]


def perform_sentiment_analysis(df, col):
    sid = SIA()

    def sentilysis(text):
        return sid.polarity_scores(" ".join(re.findall(r"\w+", text.lower())))

    df["sentiments"] = df[col].apply(sentilysis)
    df["positive"] = df["sentiments"].apply(lambda x: x["pos"] + 1 * (10 ** -6))
    df["neutral"] = df["sentiments"].apply(lambda x: x["neu"] + 1 * (10 ** -6))
    df["negative"] = df["sentiments"].apply(lambda x: x["neg"] + 1 * (10 ** -6))
    return df


def prep_comment_cols_for_db(df):
    df = df.rename(
        columns={
            "author": "user",
            "created_dt": "dt",
            "link_id": "submission_id",
        }
    )
    df["iscomment"] = 1
    return df


def prep_submission_cols_for_db(df):
    df = df.rename(
        columns={
            "author": "user",
            "created_dt": "dt",
            "link_id": "submission_id",
        }
    )
    df["submission_id"] = df["id"]
    df["parent_id"] = df["id"]
    df["iscomment"] = 0
    return df


def select_post_record_cols(df):
    return df[
        [
            "id",
            "submission_id",
            "parent_id",
            "user",
            "iscomment",
            "positive",
            "neutral",
            "negative",
            "dt",
        ]
    ]
