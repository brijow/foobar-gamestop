FROM python:3.8

WORKDIR /usr/app

ADD ./microservices/pred_producer/requirements.txt ./
RUN pip install -r requirements.txt

ADD ./setup.py ./
COPY foobar/ ./foobar/
RUN pip install -e .
COPY  ./microservices/pred_producer/ ./

CMD ["python3", "-u", "m1_predict_producer.py"]
