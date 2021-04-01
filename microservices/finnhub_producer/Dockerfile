FROM python:3.9

WORKDIR /usr/app

ADD ./requirements.txt ./
RUN pip install -r requirements.txt
ADD ./ ./

CMD ["python3", "-u", "api_client.py"]
