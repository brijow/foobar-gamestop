## Quickstart instructions

1. Clone repo
2. `cd` into directory
3. Install package, `pip install -e ./`
4. Run the program (TODO: add instructions -- maybe define a commands in Makefile for this!)

## Notes on directory structure
------------

In this project, the following directory structure is followed:

```
├── README.md
├── README.md
├── .pre-commit-config.yaml                 <-- hooks to run linters on each git commit
├── setup.cfg                               <-- linter configuration options
├── setup.py                                <-- defines the package, run 'pip install -e ./' in root dir after cloning repo to install
│
├── Makefile                                <-- TODO
├── LICENSE                                 <-- TODO
│
├── foobar_gamestop
│   ├── __init__.py
│   ├── datasets
│   │   ├── __init__.py                     <-- explicitly defines what functions in this folder are importable
│   │   ├── _base.py                        <-- general functions shared by other data specific modules
│   │   ├── _avocado_data.py                <-- logic specific for managing avocado data
│   │   ├── _reddit_data.py                 <-- logic specific for managing reddit data
│   │   └── raw                             <-- folder and contents not in version control
│   │       ├── avocado.csv
│   │       └── reddit_wsb.csv
│   └── vis                                 <-- the dash app logic lives here
│       ├── __init__.py                     <-- empty file, just defines vis to be a subpackage (importable)
│       └── app.py                          <-- does "from foobar_gamestop.datasets import load_<subject>_data"
│
├── reddit-wsb                              <- (TODO) Logic for reddit wallstreetbets
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

## Notes on code formatting (for contributors)

> **Note:** 
> This assumes you have installed black, flake8, isort, and mypy in your python environment.
> For example, if using conda: 
>
> `conda install black flake8 isort mypy`


1. There is a setup.cfg file in root of the project. This config file ensure that
   the auto-formatting / linting tools play nicely together. The tools used are the following:
   - black
   - flake8
   - isort
   - mypy

2. There is a .pre-commit-config.yaml file in the root of the project. This ensures that that
   auto-formatting tools will be run every time code is committed to ensure the formatting is
   consistent.



## Notes on naming conventions (for contributors)
------------
1. Directory names use hypen-case and reflect the logic they contain, (e.g. reddit-wsb, or finhub-gamestop, etc).
2. Python file names use snake case
3. Test file names are prefixed with 'test_', followed by the module name they are testing.
