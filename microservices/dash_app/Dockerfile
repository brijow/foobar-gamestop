FROM python:3.9

WORKDIR /usr/app

ADD ./requirements.txt ./
RUN pip install -r requirements.txt

ENV HOST="0.0.0.0"
ADD ./ ./
ENTRYPOINT ["python", "-u", "app.py"]

