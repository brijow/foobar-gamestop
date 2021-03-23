"""
Utilities to load and fetch popular datasets.
"""

from ._base import get_or_create_raw_data_dir, get_root_data_dir  # isort:skip
from ._avocado_data import load_avocado_data
from ._reddit_data import load_reddit_data

__all__ = ['get_root_data_dir',
           'get_or_create_raw_data_dir',
           'load_avocado_data',
           'load_reddit_data']
