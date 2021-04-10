#!/bin/sh

echo "Waiting for Kafka Connect to start listening on kafka-connect at $HOSTNAME ⏳"

while [ `curl -s -o /dev/null -w %{http_code} http://$HOSTNAME:${CONNECT_REST_PORT}/connectors` -eq 000 ] ; do 
    echo $(date) " Kafka Connect listener HTTP state: " $(curl -s -o /dev/null -w %{http_code} http://$HOSTNAME:${CONNECT_REST_PORT}/connectors) " (waiting for 200)"
    sleep 5 
done
nc -vz $HOSTNAME ${CONNECT_REST_PORT}
echo "\n--\n+> Creating Kafka Connect Cassandra sink"

./create-cassandra-sink.sh 

sleep infinity