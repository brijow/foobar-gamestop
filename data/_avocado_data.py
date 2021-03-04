import os

import pandas as pd

from . import get_or_create_raw_data_dir
from ._base import _fetch_all_files_from_kaggle

DATASET = 'neuromusic/avocado-prices'
LOCAL_FILE_NAME = 'avocado.csv'


def load_avocado_data(download_if_missing=True):
    """Load avocado dataset from kaggle."""

    data_dir = get_or_create_raw_data_dir()
    file_path = os.path.join(data_dir, LOCAL_FILE_NAME)

    if not os.path.exists(file_path):
        if not download_if_missing:
            raise IOError("Data not found and `download_if_missing` is False")

        _fetch_all_files_from_kaggle(dataset=DATASET, path=data_dir, unzip=True)

    file_path = os.path.join(data_dir, LOCAL_FILE_NAME)
    avocado_df = pd.read_csv(file_path)
    return avocado_df
