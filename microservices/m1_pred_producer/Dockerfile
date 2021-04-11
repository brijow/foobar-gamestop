FROM python:3.8

WORKDIR /usr/app

ADD ./microservices/m1_pred_producer/requirements.txt ./
RUN pip install -r requirements.txt

ADD  ./microservices/m1_pred_producer/ ./
ADD ./foobar/db_utils/cassandra_utils.py ./
ADD ./foobar.prediction.predictor/ ./
ADD ./foobar/model/lstm.py ./
ADD ./foobar/model/model_loader.py ./

CMD ["python3", "-u", "m1_predict_producer.py"]
