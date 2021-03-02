## Notes on code formatting

1. There is a setup.cfg file in root of the project. This config file ensure that
   the auto-formatting / linting tools play nicely together. The tools used are the following:
   - black
   - flake8
   - isort
   - mypy

2. There is a .pre-commit-config.yaml file in the root of the project. This ensures that that
   auto-formatting tools will be run every time code is committed to ensure the formatting is
   consistent.


> **Note:** 
> This assumes you have installed black, flake8, isort, and mypy in your python environment.
> For example, if using conda: 
>
> `conda install black flake8 isort mypy`


## Notes on directory structure
------------

In this project, the following directory structure is followed:

```
├── LICENSE
├── README.md
├── Makefile
├── .pre-commit-config.yaml
├── setup.cfg
│
├── data                                    <- All data sets reside here, but dir not in version control
│   ├── raw                                 <- Raw data, populated by various make_dataset.py scripts
│   │   ├── reddit_wsb_raw_jan20.csv
│   │   ├── reddit_wsb_raw_feb20.csv
│   │   ├── ...
│   │   ├── gs_prices_raw_jan20.csv
│   │   ├── gs_prices_raw_jan20.csv
│   │   └── ... etc.
│   └── processed                           <- Processed data sets (raw data cleaned / aggregated)
│       ├── reddit_wsb_gs_pos_jan20.csv
│       ├── reddit_wsb_gs_neg_jan20.csv
│       └── test_module_one.py
│
├── reddit-wsb                              <- Logic for reddit wallstreetbets
│   ├── __init__.py
│   ├── __main__.py                         <- Driver code
│   ├── reddit_post.py                      <- Module defining a RedditPost class
│   ├── data                                <- Scripts to manage reddit-wsb data
│   │   ├── download_data.py                <- Download reddit wallstreetbets data and save in root data/raw dir
│   │   └── extract_gs_sentiment.py         <- Extract sentiment data from raw wallstreetbets data
│   └── test                                <- Unit tests for modules in reddit-wsb dir (optional)
│       ├── __init__.py
│       └── test_extract_gs_sentiment.py    <- Tests for logic in extract_gs_sentiment.py
│
└── ... more-services-here ...
```

> **Note:** 
Directories are best kept shallow if possible, and organized somewhat consistently.
E.g., if a piece of logic needs to download some data, it has a data sub dir and a download_data.py module which
saves the file to the top level data directory, (i.e., gamestop/data/raw/your_data_here.csv).

A few sources of inspiration for this directory structure:

1. The cookiecutter-data-science directory structure: https://drivendata.github.io/cookiecutter-data-science/#directory-structure
2. A simpler cookiecutter template, with more focus on tests: https://github.com/sourcery-ai/python-best-practices-cookiecutter, (see also https://sourcery.ai/blog/python-best-practices/)
3. The docker directory from Aurelien Geron's git repo for his Hands on ML with Sklearn and TF book: https://github.com/ageron/handson-ml2/tree/master/docker
4. The directory structure used in our blog post repo: https://csil-git1.cs.surrey.sfu.ca/733-foobar/foobar-kafka


## Notes on naming conventions
------------
1. Directory names use hypen-case and reflect the logic they contain, (e.g. reddit-wsb, or finhub-gamestop, etc).
2. Python file names use snake case
3. Test file names are prefixed with 'test_', followed by the module name they are testing.
