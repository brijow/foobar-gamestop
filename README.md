## Directory structure plan
------------

There are a few sources of inspiration for directory structures:

1. The cookiecutter-data-science directory structure: https://drivendata.github.io/cookiecutter-data-science/#directory-structure
2. A simpler cookiecutter template, with more focus on tests: https://github.com/sourcery-ai/python-best-practices-cookiecutter, (see also https://sourcery.ai/blog/python-best-practices/)
3. The docker directory from Aurelien Geron's git repo for his Hands on ML with Sklearn and TF book: https://github.com/ageron/handson-ml2/tree/master/docker
4. The directory structure used in our blog post repo: https://csil-git1.cs.surrey.sfu.ca/733-foobar/foobar-kafka


### WIP 

```
├── LICENSE
│
├── README.md
│
├── Makefile
│
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- General purpose Jupyter notebooks
│
├── service-one
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── service-one-code
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   └── module_one.py
│   └── test
│       ├── __init__.py
│       └── test_module_one.py
│
├── service-two
│   └── ... etc.
│
└── ... more-services-here ...
```
