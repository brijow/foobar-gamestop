"""
Utilities to load and fetch popular datasets.
"""

from ._base import get_or_create_raw_data_dir, get_root_data_dir  # isort:skip
from ._base import load_kaggle_data

__all__ = ['get_root_data_dir',
           'get_or_create_raw_data_dir',
           'load_kaggle_data']
