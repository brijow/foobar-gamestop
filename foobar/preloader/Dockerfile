FROM python:3.8
WORKDIR /usr/app
ADD ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
ADD ./ ./
CMD ["/usr/app/keep-busy.sh"]
