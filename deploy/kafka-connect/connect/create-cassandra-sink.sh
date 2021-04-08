#!/bin/sh


export finnhubsinkconfig='{
  "name": "finnhubsink",
  "config":{
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "contactPoints": "'${CASSANDRA_HOST}'",
    "auth.username": "'${CASSANDRA_USERNAME}'",
    "auth.password": "'${CASSANDRA_PASSWORD}'",
    "tasks.max": "2",
    "topics": "'${FINNHUB_TOPIC}'",
    "loadBalancing.localDc": "datacenter1",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",  
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "topic.'${FINNHUB_TOPIC}'.kafkapipeline.gamestop.mapping": "id=value.uuid, timestamp=value.timestamp, close_price=value.close_price, open_price=value.open_price, high_price=value.high_price, low_price=value.low_price, volume=value.volume",
    "topic.'${FINNHUB_TOPIC}'.kafkapipeline.gamestop.consistencyLevel": "LOCAL_QUORUM"
  }
}'
# {"close_price":174.49,"high_price":174.49,"low_price":174.49,"open_price":174.49,"status":"ok","volume":125,"uuid":"408d7cbb-0989-4d31-ac4c-ccb330455e4e"}
export weathersinkconfig='{
  "name": "weathersink",
  "config": {
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "contactPoints": "'${CASSANDRA_HOST}'",
    "auth.username": "'${CASSANDRA_USERNAME}'",
    "auth.password": "'${CASSANDRA_PASSWORD}'",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",  
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "tasks.max": "2",
    "topics": "weather",
    "loadBalancing.localDc": "datacenter1",
    "topic.weather.kafkapipeline.weatherreport.mapping": "location=value.location, forecastdate=value.report_time, description=value.description, temp=value.temp, feels_like=value.feels_like, temp_min=value.temp_min, temp_max=value.temp_max, pressure=value.pressure, humidity=value.humidity, wind=value.wind, sunrise=value.sunrise, sunset=value.sunset",
    "topic.weather.kafkapipeline.weatherreport.consistencyLevel": "LOCAL_QUORUM"
  }
}'

echo "Starting Finnhub Sink for ${CASSANDRA_HOST}"
curl -s \
     -X POST http://${HOSTNAME}:${CONNECT_REST_PORT}/connectors \
     -H "Content-Type: application/json" \
     -d "$finnhubsinkconfig"
# echo "Starting Weather Sink"
# curl -s \
#      -X POST http://${HOSTNAME}:${CONNECT_REST_PORT}/connectors \
#      -H "Content-Type: application/json" \
#      -d "$weathersinkconfig"
echo "Done."
