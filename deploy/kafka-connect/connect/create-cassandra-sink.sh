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
    "topic.'${FINNHUB_TOPIC}'.kafkapipeline.gamestop.mapping": "hour=value.hour, close_price=value.close_price, open_price=value.open_price, high_price=value.high_price, volume=value.volume, low_price=value.low_price",
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
    "topic.'${REDDIT_TAG_TOPIC}'.kafkapipeline.tag.mapping": "id=value.id, post_id=value.post_id, tag_token=value.tag",
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
    "topic.'${WIDE_TOPIC}'.kafkapipeline.wide.mapping": "prediction_reddit='"value.prediction_reddit"',hour='"value.hour"'",
    "topic.'${WIDE_TOPIC}'.kafkapipeline.wide.consistencyLevel": "LOCAL_QUORUM"
  }
}'
# prediction_wide='"value.prediction_wide"',prediction_finn='"value.prediction_finn"',high_price='"value.high_price"',close_price='"value.close_price"',low_price='"value.low_price"',cnt_gme_comments='"value.cnt_gme_comments"',cnt_gme_post='"value.cnt_gme_post"',cnt_gme_tag='"value.cnt_gme_tag"',cnt_gme_user='"value.cnt_gme_user"',avg_gme_post_neu='"value.avg_gme_post_neu"',avg_gme_post_neg='"value.avg_gme_post_neg"',avg_gme_post_pos='"value.avg_gme_post_pos"',cnt_all_comments='"value.cnt_all_comments"',cnt_all_post='"value.cnt_all_post"',cnt_all_tag='"value.cnt_all_tag"',cnt_all_user='"value.cnt_all_user"',avg_all_post_neu='"value.avg_all_post_neu"',avg_all_post_neg='"value.avg_all_post_neg"',avg_all_post_pos='"value.avg_all_post_pos"',open_price='"value.open_price"',volume='"value.volume"',
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
