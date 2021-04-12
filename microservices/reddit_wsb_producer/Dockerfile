FROM python:3.8

WORKDIR /usr/app
RUN apt-get update && \
    apt-get -y install netcat vim && \
    mkdir -p foobar/data_loader foobar/preprocessing

ADD ./microservices/reddit_wsb_producer/requirements.txt ./
RUN pip install -r requirements.txt && \
    python -m nltk.downloader vader_lexicon && \
    python -m spacy download en_core_web_sm

ADD ./microservices/reddit_wsb_producer/ ./
ADD ./setup.py ./

COPY foobar/ ./foobar/
RUN pip install -e .

# ENTRYPOINT [ "/bin/bash", "-c", "/usr/app/kafka-wait.sh"]
# CMD ["python3", "-u", "wsb_driver.py"]
CMD ["python3", "-u", "wsb_comments_producer.py"]