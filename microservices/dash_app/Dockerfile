FROM python:3.9

WORKDIR /usr/app

ENV HOST="0.0.0.0"
ADD ./microservices/dash_app/requirements.txt ./
RUN pip install -r requirements.txt

ADD ./setup.py ./
COPY foobar/ ./foobar/
RUN pip install -e .
COPY  ./microservices/dash_app/ ./


ENTRYPOINT ["python", "-u", "app.py"]
