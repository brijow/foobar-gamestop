## Developer instructions 
1. Install the following packages in your development environment before making git commmits:
> `conda install black flake8 isort mypy pre-commit`
2. Clone repo `cd` into root directory of project
3. Install the pre-commit configuration
> `pre-commit install`
4. Install the foobar_gamestop code as python package, `pip install -e ./` (again from root of project)
5. Make your changes now as usual on a branch and when you run `git commit` the linters will be run to auto-format your code to PEP8


## Notes on directory structure
------------

In this project, the following directory structure is followed:

```
.
├── setup.py
├── setup.cfg
├── README.md
├── .pre-commit-config.yaml
├── .gitignore
├── foobar_gamestop
│   ├── __init__.py
│   ├── vis
│   │   ├── __init__.py
│   │   ├── components.py
│   │   └── app.py
│   ├── reddit_wsb
│   │   ├── __init__.py
│   │   ├── producer
│   │   │   ├── wsb_posts_producer.py
│   │   │   ├── wsb_comments_producer.py
│   │   │   ├── requirements.txt
│   │   │   ├── .env
│   │   │   ├── Dockerfile
│   │   │   └── docker-compose.yml
│   │   └── data_utils
│   │       ├── __init__.py
│   │       ├── praw.ini
│   │       ├── _reddit_data.py
│   │       └── _kaggle_wsb_get_data.py
│   ├── notebooks
│   │   └── wsb-senti-analysis.ipynb
│   ├── datasets
│   │   ├── __init__.py
│   │   ├── _base.py
│   │   └── samples
│   │       ├── submission_sample_object.json
│   │       ├── stock_candle_timeseries.csv
│   │       ├── filling_sentiment_ts.csv
│   │       └── comment_sample_object.json
│   └── avocados
│       ├── __init__.py
│       └── data_utils
│           ├── __init__.py
│           └── _avocado_data.py
└── finnhub-producer
    ├── requirements.txt
    ├── Dockerfile
    ├── docker-compose.yml
    ├── api_client.py
    └── api.cfg
```

## Notes on naming conventions
------------
1. Directory names use hypen-case and reflect the logic they contain, (e.g. reddit-wsb, or finhub-gamestop, etc).
2. Python file names use snake case
3. Test file names are prefixed with 'test_', followed by the module name they are testing.
