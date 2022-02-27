# foobar-gamestop, or "Real time data mining r/WallStreetBets"


<p align="center">
    <img src="https://user-images.githubusercontent.com/11220949/155862781-4763b6dc-f06e-4769-ad68-a5f8253ec418.png">
</p>


## Running the application

> The bad news: Sorry, the app is no longer live (running our K8s cluster in EKS was too costly).
> 
> The good news: You can still follow the instructions below to bring up your own EKS cluster (assuming you have installed the aws cli tools for managing an EKS cluster), or, just clone the repo (instructions below) and run a static version of the dash app to visualize some [sample data in a csv](https://raw.githubusercontent.com/brijow/foobar-gamestop/demo/microservices/dash_app/wide1.csv?token=GHSAT0AAAAAABQ45KNS7BK4YINMZ7V7BIVQYRD7WZA) ! For the latter:
>
> ```
> git clone https://github.com/brijow/foobar-gamestop.git
> cd foobar-gamestop/microservices/dash_app
> pip install -r requirements
> python app.py
> ```
>
> You can now view the dash app in your browser, (link is displayed in your terminal, should be http://127.0.0.1:8888/)



## Quick start instructions 
1. Install the following packages in your development environment before making git commmits:
> `conda install black flake8 isort mypy pre-commit`
2. Clone repo `cd` into root directory of project
3. Install the pre-commit configuration
> `pre-commit install`
4. Install the foobar_gamestop code as python package, `pip install -e ./` (again from root of project)
5. Make your changes now as usual on a branch and when you run `git commit` the linters will be run to auto-format your code to PEP8

## EKS cluster
You'll have to configure access to the cluster with eksctl and kubectl.
(more info coming.)

All commands have to be run from gamestop/deploy root directory **on the master branch**

### Creating the EKS cluster
```
eksctl create cluster -f cluster.yaml

```

### Install the application using Helm

```
helm install shortsqueeze ./

```

### Connect to cassandra
```
kubectl exec --stdin --tty shortsqueeze-cassandra-0 -- /bin/bash
cqlsh --cqlversion=3.4.4 -u admin -p welcome1

```

### Uninstalling the application
```
helm delete shortsqueeze

```
### Delete the EKS cluster
```
kubectl delete cluster -f cluster.yaml
```

### Overview of project tree structure
------------

```
.
├── setup.py
├── setup.cfg
├── README.md
├── LICENSE.txt
├── .pre-commit-config.yaml
├── .gitignore
│
├── foobar
│   ├── __init__.py
│   ├── trainer
│   │   ├── __init__.py
│   │   ├── _base_trainer.py
│   │   └── autoencoder_trainer.py
│   ├── model
│   │   ├── __init__.py
│   │   └── _base_model.py
│   ├── data_loader
│   │   ├── __init__.py
│   │   ├── _reddit_data.py
│   │   ├── _kaggle_wsb_get_data.py
│   │   ├── _finnhub_data.py
│   │   ├── _base.py
│   │   └── conf
│   │      ├── praw.ini
│   │      └── kaggle.json
│   └── data
│       ├── samples
│       │   ├── submission_sample_object.json
│       │   ├── stock_candle_timeseries.csv
│       │   ├── shortinterest.csv.zip
│       │   ├── README.md
│       │   ├── filling_sentiment_ts.csv
│       │   └── comment_sample_object.json
│       ├── raw
│       │   └── README.md
│       └── processed
│           └── README.md
│
├── notebooks
│   └── wsb-senti-analysis.ipynb
│
├── microservices
│   ├── reddit_wsb_producer
│   │   ├── wsb_posts_producer.py
│   │   ├── wsb_comments_producer.py
│   │   ├── requirements.txt
│   │   ├── .env
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   ├── finnhub_producer
│   │   ├── requirements.txt
│   │   ├── finnancial_data_producer.py
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   └── dash_app
│       ├── __init__.py
│       ├── components.py
│       ├── app.py
│       └── figures
│           ├── __init__.py
│           ├── network.py
│           └── line_chart.py
│
└── deploy
    └── README.md

## Notes on naming conventions
------------
1. Python file names use snake case
2. Test file names are prefixed with 'test_', followed by the module name they are testing.
