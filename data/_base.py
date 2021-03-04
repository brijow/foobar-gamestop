"""
Base IO code for all datasets.
"""

import os

from kaggle.api.kaggle_api_extended import KaggleApi


def get_root_data_dir():
    """Return the path of the top level data dir."""
    root_data_dir = os.environ.get('GAMESTOP_ROOT_DATA_DIR',
                                   os.path.join('.', 'data'))

    dir_path = os.path.expanduser(root_data_dir)

    return dir_path


def get_or_create_raw_data_dir():
    """Return the path of the raw data dir."""
    raw_data_dir = os.environ.get('GAMESTOP_RAW_DATA_DIR',
                                  os.path.join(get_root_data_dir(), 'raw'))

    dir_path = os.path.expanduser(raw_data_dir)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    return dir_path


def _fetch_file_from_kaggle(dataset, file_name, path=None, force=False):
    """Download single file from a kaggle dataset.

    Signature of method call
    ------------------------
    dataset_download_file(dataset, file_name, path=None, force=False, quiet=True)

    See here for more info: https://stackoverflow.com/a/60309843/8196202
    """
    api = KaggleApi()
    api.authenticate()
    api.dataset_download_file(dataset=dataset, file_name=file_name,
                              path=path, force=force)


def _fetch_all_files_from_kaggle(dataset, path=None, force=False, unzip=False):
    """Download all files from a kaggle dataset.

    Signature of method call
    ------------------------
    dataset_download_files(dataset, path=None, force=False, quiet=True, unzip=False)

    See here for more info: https://stackoverflow.com/a/60309843/8196202
    """
    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files(dataset=dataset, path=path, force=force, unzip=unzip)
