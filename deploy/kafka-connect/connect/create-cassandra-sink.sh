#!/bin/sh


export finnhubsinkconfig='{
  "name": "finnhubsink",
  "config":{
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "contactPoints": "'${CASSANDRA_HOST}'",
    "auth.username": "'${CASSANDRA_USERNAME}'",
    "auth.password": "'${CASSANDRA_PASSWORD}'",
    "tasks.max": "1",
    "topics": "'${FINNHUB_TOPIC}'",
    "loadBalancing.localDc": "datacenter1",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",  
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "topic.'${FINNHUB_TOPIC}'.kafkapipeline.gamestop.mapping": "id=value.uuid, timestamp_=value.timestamp_, close_price=value.close_price, open_price=value.open_price, high_price=value.high_price, low_price=value.low_price, volume=value.volume, prediction=value.prediction",
    "topic.'${FINNHUB_TOPIC}'.kafkapipeline.gamestop.consistencyLevel": "LOCAL_QUORUM"
  }
}'

export redditpostsink='{
  "name": "redditpostsink",
  "config": {
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "contactPoints": "'${CASSANDRA_HOST}'",
    "auth.username": "'${CASSANDRA_USERNAME}'",
    "auth.password": "'${CASSANDRA_PASSWORD}'",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",  
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "tasks.max": "1",
    "topics": "'${REDDIT_POST_TOPIC}'",
    "loadBalancing.localDc": "datacenter1",
    "topic.'${REDDIT_POST_TOPIC}'.kafkapipeline.post.mapping": "id=value.id, submission_id=value.submission_id, parent_id=value.parent_id, username=value.user, iscomment=value.iscomment, positive=value.positive, neutral=value.neutral, negative=value.negative, dt=value.dt",
    "topic.'${REDDIT_POST_TOPIC}'.kafkapipeline.post.consistencyLevel": "LOCAL_QUORUM"
  }
}'

export reddittagsink='{
  "name": "reddittagsink",
  "config": {
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "contactPoints": "'${CASSANDRA_HOST}'",
    "auth.username": "'${CASSANDRA_USERNAME}'",
    "auth.password": "'${CASSANDRA_PASSWORD}'",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",  
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "tasks.max": "1",
    "topics": "'${REDDIT_TAG_TOPIC}'",
    "loadBalancing.localDc": "datacenter1",
    "topic.'${REDDIT_TAG_TOPIC}'.kafkapipeline.tag.mapping": "post_id=value.post_id, tag_token=value.tag",
    "topic.'${REDDIT_TAG_TOPIC}'.kafkapipeline.tag.consistencyLevel": "LOCAL_QUORUM"
  }
}'

export widesink='{
  "name": "widesink",
  "config": {
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "contactPoints": "'${CASSANDRA_HOST}'",
    "auth.username": "'${CASSANDRA_USERNAME}'",
    "auth.password": "'${CASSANDRA_PASSWORD}'",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",  
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "tasks.max": "1",
    "topics": "'${WIDE_TOPIC}'",
    "loadBalancing.localDc": "datacenter1",
    "topic.'${WIDE_TOPIC}'.kafkapipeline.wide.mapping": "hour=value.hour, id=value.id, positive_all=value.positive_all, negative_all=value.negative_all, neutral_all=value.neutral_all, user_count_all=value.user_count_all, tag_count_all=value.tag_count_all, total_count_all=value.total_count_all, comments_count_all=value.comments_count_all, positive_gme=value.positive_gme, negative_gme=value.negative_gme, neutral_gme=value.neutral_gme, user_count_gme=value.user_count_gme, tag_count_gme=value.tag_count_gme, total_count_gme=value.total_count_gme, comments_count_gme=value.comments_count_gme, volume=value.volume, closeprice=value.closeprice, highprice=value.highprice, openprice=value.openprice, prediction=value.prediction",
    "topic.'${WIDE_TOPIC}'.kafkapipeline.wide.consistencyLevel": "LOCAL_QUORUM"
  }
}'

# hour,id,positive_all,negative_all,neutral_all,user_count_all,tag_count_all,
# total_count_all,comments_count_all,positive_gme,negative_gme,neutral_gme,
# user_count_gme,tag_count_gme,total_count_gme,comments_count_gme,volume,closeprice,
# highprice,openprice,prediction

echo "Starting Finnhub sink for ${CASSANDRA_HOST}"
curl -s \
     -X POST http://${HOSTNAME}:${CONNECT_REST_PORT}/connectors \
     -H "Content-Type: application/json" \
     -d "$finnhubsinkconfig"

echo "Starting Reddit post sink"
curl -s \
     -X POST http://${HOSTNAME}:${CONNECT_REST_PORT}/connectors \
     -H "Content-Type: application/json" \
     -d "$redditpostsink"

echo "Starting Reddit tag sink"
curl -s \
     -X POST http://${HOSTNAME}:${CONNECT_REST_PORT}/connectors \
     -H "Content-Type: application/json" \
     -d "$reddittagsink"

echo "Starting wide table sink"
curl -s \
     -X POST http://${HOSTNAME}:${CONNECT_REST_PORT}/connectors \
     -H "Content-Type: application/json" \
     -d "$widesink"

echo "Done."
