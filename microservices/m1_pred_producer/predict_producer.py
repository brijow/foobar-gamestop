import numpy as nu
import pandas as pd
from kafka import KafkaProducer
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import time
import torch
import boto3
import botocore
import os

BUCKET = 'bb-s3-bucket-cmpt733'
MODEL_FILE = 'm1.pth'

s3_client = boto3.client('s3')
s3 = boto3.resource('s3')
bucket = s3.Bucket(BUCKET)
for my_bucket_object in bucket.objects.all():
    print(my_bucket_object)

s3_client.download_file(BUCKET, MODEL_FILE, "./m1.pth")
# model = open(MODEL_FILE).read()
# checkpoint = torch.load('./checkpoint/{}.pth'.format(args.net))
#         net.load_state_dict(checkpoint['net'])
#         best_acc = checkpoint['acc']

# obj = s3.Object(BUCKET, MODEL_FILE)

# Kafka producer
KAFKA_BROKER_URL = (
    os.environ.get("KAFKA_BROKER_URL")
    if os.environ.get("KAFKA_BROKER_URL")
    else "localhost:9092"
)
TOPIC_NAME = (
    os.environ.get("TOPIC_NAME") if os.environ.get("TOPIC_NAME") else "m1-pred"
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER_URL,
    value_serializer=lambda x: x.encode("utf8"),
    api_version=(0, 11, 5),
)
# read historical data from cassandra and make predictions
# # X.shape[0]

# while True:
#     cloud_config = {
#     'secure_connect_bundle': '/path/to/secure-connect-dbname.zip'
#     }
#     auth_provider = PlainTextAuthProvider(username='user', password='pass')
#     cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
#     session = cluster.connect()
#     rows = session.execute('SELECT name, age, email FROM users')
#     for user_row in rows:
#         print(user_row.name, user_row.age, user_row.email)

#     session.execute(
#         """
#         INSERT INTO users (name, credits, user_id)
#         VALUES (%s, %s, %s)
#         """,
#         ("John O'Reilly", 42, uuid.uuid1())
#     )
#     with torch.no_grad():
#         model.eval()
#         x.to(device)
#         model.init_hidden(x.shape[0])
#         y_pred = model(x)
#         close_price = y_pred.cpu().numpy().flatten()
#         print(f"Next hour close price predicted: {close_price}")
#         producer.send(TOPIC_NAME, value=close_price)
#         time.sleep(3600)
