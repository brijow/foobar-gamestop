"""
Base IO code for all datasets.
"""

import configparser
import os
from pathlib import Path

import pandas as pd
import requests


def get_project_root():
    return Path(__file__).parent.parent


def get_root_data_dir():
    """Return the path of the top level data dir."""
    root_data_dir = os.environ.get(
        "FOOBAR_ROOT_DATA_DIR", os.path.join(get_project_root(), "data")
    )

    dir_path = os.path.expanduser(root_data_dir)

    return dir_path


def get_or_create_raw_data_dir():
    """Return the path of the raw data dir."""
    raw_data_dir = os.environ.get(
        "FOOBAR_RAW_DATA_DIR", os.path.join(get_root_data_dir(), "raw")
    )

    dir_path = os.path.expanduser(raw_data_dir)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    return dir_path


def get_or_create_processed_data_dir():
    """Return the path of the processed data dir."""
    data_dir = os.environ.get(
        "FOOBAR_PROCESSED_DATA_DIR", os.path.join(get_root_data_dir(), "processed")
    )

    dir_path = os.path.expanduser(data_dir)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    return dir_path


def get_data_loader_conf_dir():
    """Return the path of the data_loader config dir."""
    data_loader_conf_dir = os.path.join(get_project_root(), "data_loader", "conf")

    dir_path = os.path.expanduser(data_loader_conf_dir)

    return dir_path


def get_praw_conf_dir():
    get_data_loader_conf_dir()


def set_kaggle_conf_dir():
    os.environ["KAGGLE_CONFIG_DIR"] = get_data_loader_conf_dir()


def _fetch_file_from_kaggle(dataset, file_name, path=None, force=False):
    """Download single file from a kaggle dataset.

    Signature of method call
    ------------------------
    dataset_download_file(dataset, file_name, path=None, force=False, quiet=True)

    See here for more info: https://stackoverflow.com/a/60309843/8196202
    """
    set_kaggle_conf_dir()
    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()
    api.dataset_download_file(
        dataset=dataset, file_name=file_name, path=path, force=force
    )


def _fetch_all_files_from_kaggle(dataset, path=None, force=False, unzip=False):
    """Download all files from a kaggle dataset.

    Signature of method call
    ------------------------
    dataset_download_files(dataset, path=None, force=False, quiet=True, unzip=False)

    See here for more info: https://stackoverflow.com/a/60309843/8196202
    """
    set_kaggle_conf_dir()
    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files(dataset=dataset, path=path, force=force, unzip=unzip)


def load_kaggle_data(
    local_fname,
    dataset,
    unzip,
    single_file=False,
    download_if_missing=True,
    force=False,
    chunksize=None,
    usecols=None,
):
    """Load a dataset from kaggle."""

    data_dir = get_or_create_raw_data_dir()
    file_path = os.path.join(data_dir, local_fname)

    if not os.path.exists(file_path):
        if not download_if_missing:
            raise IOError("Data not found and `download_if_missing` is False")

        if single_file:
            _fetch_file_from_kaggle(
                dataset=dataset, file_name=local_fname, path=data_dir, force=force
            )
        else:
            _fetch_all_files_from_kaggle(
                dataset=dataset, path=data_dir, force=force, unzip=unzip
            )

    file_path = os.path.join(data_dir, local_fname)

    return pd.read_csv(
        file_path,
        chunksize=chunksize,
        usecols=usecols,
        low_memory=False,
    )


def _fetch_json_from_finhubb():
    data_dir = get_or_create_raw_data_dir()

    # Finnhub API config
    config = configparser.ConfigParser()
    config.read(os.path.join(get_data_loader_conf_dir(), "finnhub.cfg"))
    api_credential = config["api_credential"]
    AUTH_TOKEN = api_credential["auth_token"]

    r = requests.get(
        f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={AUTH_TOKEN}"
    )
    df = pd.DataFrame.from_records(r.json())
    sf = (df["description"] + df["symbol"]).str.split().explode()
    sf = sf.str.replace(r"\W", "", regex=True).str.upper().drop_duplicates()
    sf = sf[sf.str.len() > 2]
    sf.to_csv(os.path.join(data_dir, "all_stock_tags.csv"), index=False)


def load_all_stock_tags():
    data_dir = get_or_create_raw_data_dir()
    file_path = os.path.join(data_dir, "all_stock_tags.csv")

    if not os.path.exists(file_path):
        _fetch_json_from_finhubb()

    file_path = os.path.join(data_dir, "all_stock_tags.csv")
    df = pd.read_csv(file_path, names=["finnhub_tags"], header=0)
    return df
