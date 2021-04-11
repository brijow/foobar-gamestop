FROM python:3.8

WORKDIR /usr/app

ADD ./requirements.txt ./
RUN pip install -r requirements.txt
ADD ./ ./
ADD ./foobar.db_utils.cassandra_utils.py ./
ADD ./foobar.prediction.predictor.py ./
ADD ./foobar.model.model_loader.py ./
ADD ./foobar.model.lstm.py ./


CMD ["python3", "-u", "m1_predict_producer.py"]
