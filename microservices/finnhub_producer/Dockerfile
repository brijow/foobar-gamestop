FROM python:3.9

WORKDIR /usr/app
RUN apt-get update && \
    apt-get -y install netcat vim
ADD ./requirements.txt ./
RUN pip install -r requirements.txt
ADD ./ ./
RUN chmod +x *.sh
CMD [ "/bin/bash", "-c", "/usr/app/kafka-wait.sh"]
