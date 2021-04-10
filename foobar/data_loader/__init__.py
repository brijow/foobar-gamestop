"""
Utilities to load and fetch popular datasets.
"""

from ._base import (
    get_or_create_processed_data_dir,
    get_or_create_raw_data_dir,
    get_root_data_dir,
    load_all_stock_tags,
    load_stock_ticker_tags,
)
from ._reddit_data import load_reddit_comments_data_reader, load_reddit_submissions_data

__all__ = [
    "get_root_data_dir",
    "get_or_create_raw_data_dir",
    "get_or_create_processed_data_dir",
    "load_reddit_submissions_data",
    "load_reddit_comments_data_reader",
    "load_all_stock_tags",
    "load_stock_ticker_tags",
]
