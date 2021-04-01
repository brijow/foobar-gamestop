"""
Utilities to load and fetch popular datasets.
"""

from ._base import get_root_data_dir
from ._reddit_data import load_reddit_data


__all__ = [
    "get_root_data_dir",
    "load_reddit_data",
]
