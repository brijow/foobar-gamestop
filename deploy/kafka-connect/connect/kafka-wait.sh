#!/bin/bash

test="${CONNECT_BOOTSTRAP_SERVERS/:/ }"

cmd=`nc -w 2 -vz $test`
while [[ $? -eq 1 ]] ; do 
    echo $(date) " Waiting for Kafka listener state at $test"
    sleep 5
    cmd=`nc -w 2 -vz $test`
done

echo $(date) " Launching Kafka Connect worker"
/etc/confluent/docker/run &

/usr/app/start-and-wait.sh

# sleep infinity
