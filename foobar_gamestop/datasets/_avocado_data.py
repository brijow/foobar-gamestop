from ._base import _load_kaggle_data

DATASET = 'neuromusic/avocado-prices'
LOCAL_FILE_NAME = 'avocado.csv'


def load_avocado_data(download_if_missing=True):
    """Load avocado dataset from kaggle."""
    avocado_df = _load_kaggle_data(local_fname=LOCAL_FILE_NAME,
                                   dataset=DATASET,
                                   unzip=True,
                                   download_if_missing=download_if_missing)
    return avocado_df
