#!/usr/bin/env python

from setuptools import setup

setup(
    name="foobar",
    version="1.0",
    # list folders, not files
    packages=[
        "foobar",
        "foobar.data_loader",
        "foobar.db_utils",
        "foobar.trainer",
        "foobar.model",
    ],
    install_requires=[
        "black",
        "isort",
        "flake8",
        "mypy",
        "pandas",
        "numpy",
        "kaggle",
        "praw",
        "finnhub-python",
        "torch",
        "SQLAlchemy",
        "spacy",
        "nltk"
    ],
)
