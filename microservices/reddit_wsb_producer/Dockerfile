FROM python:3.8

WORKDIR /usr/app

COPY ../../foobar/data_loader/* foobar/data_loader/
COPY ../../foobar/preprocessing/* foobar/data_loader/

ADD ./requirements.txt ./
RUN pip install -r requirements.txt
ADD ./ ./

CMD ["python3", "-u", "wsb_driver.py"]
