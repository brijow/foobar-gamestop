## Quickstart instructions

1. Clone repo
2. `cd` into directory
3. Install package, `pip install -e ./`
4. Run the program (TODO: add instructions -- maybe define a commands in Makefile for this!)

## Notes on directory structure
------------

In this project, the following directory structure is followed:

```
.
├── .gitignore
├── .pre-commit-config.yaml
├── README.md
├── foobar_gamestop
│   ├── __init__.py
│   ├── avocados
│   │   ├── __init__.py
│   │   └── data_utils
│   │       ├── __init__.py
│   │       └── _avocado_data.py
│   ├── datasets
│   │   ├── __init__.py
│   │   ├── _base.py
│   │   ├── raw
│   │   │   ├── avocado.csv
│   │   │   └── reddit_wsb.csv
│   │   └── samples
│   │       ├── comment_sample_object.json
│   │       └── submission_sample_object.json
│   ├── notebooks
│   │   └── wsb-senti-analysis.ipynb
│   ├── reddit_wsb
│   │   ├── __init__.py
│   │   ├── data_utils
│   │   │   ├── __init__.py
│   │   │   ├── _kaggle_wsb_get_data.py
│   │   │   ├── _reddit_data.py
│   │   │   └── praw.ini
│   │   └── producer
│   │       ├── .env
│   │       ├── Dockerfile
│   │       ├── docker-compose.yml
│   │       ├── requirements.txt
│   │       ├── wsb_comments_producer.py
│   │       └── wsb_posts_producer.py
│   └── vis
│       ├── __init__.py
│       └── app.py
├── setup.cfg
└── setup.py
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
