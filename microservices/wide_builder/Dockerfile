FROM python:3.8

WORKDIR /usr/app

ADD ./microservices/wide_builder/requirements.txt ./
RUN pip install -r requirements.txt

ADD  ./microservices/wide_builder/ ./
ADD ./foobar/db_utils/* ./
ADD ./foobar/data_loader/* ./

CMD ["python3", "-u", "wide_maker.py"]
