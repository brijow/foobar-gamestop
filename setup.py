#!/usr/bin/env python

from setuptools import setup

setup(
    name="foobar_gamestop",
    version="1.0",
    # list folders, not files
    packages=[
        "foobar_gamestop",
        "foobar_gamestop.datasets",
        "foobar_gamestop.reddit_wsb",
        "foobar_gamestop.reddit_wsb.data_utils",
        "foobar_gamestop.avocados",
        "foobar_gamestop.avocados.data_utils",
        "foobar_gamestop.vis",
    ],
)
