#!/bin/bash

test="${KAFKA_BROKER_URL/:/ }"

cmd=`nc -w 2 -vz $test`
while [[ $? -eq 1 ]] ; do 
    echo $(date) " Waiting for Kafka listener state at $test"
    sleep 5
    $cmd
done

echo "Launching Finnhub worker"

python3 finnancial_data_producer.py &

sleep infinity
