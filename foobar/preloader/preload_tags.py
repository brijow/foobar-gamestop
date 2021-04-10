import io
import os
import sys
from cassandra.cluster import Cluster, BatchStatement, ConsistencyLevel, uuid
from cassandra.auth import PlainTextAuthProvider
import boto3
import pandas as pd
import zipfile

print("Starting Reddit tags preloader")

CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST")
CASSANDRA_USER = os.environ.get("CASSANDRA_USER")
CASSANDRA_PWD = os.environ.get("CASSANDRA_PWD")
KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
BATCH_SIZE = int(os.environ.get("BATCH_SIZE"))

session = boto3.Session(
                    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=os.environ['AWS_SECRET_KEY'],
                    region_name=os.environ['REGION_NAME'])
                    
s3 = session.resource('s3')
bucket = s3.Bucket(BUCKET_NAME)
print("Reading tags from bucket")
tagsobj = bucket.Object(key='tags.csv')
response = tagsobj.get()
tagsdf = pd.read_csv(io.BytesIO(response['Body'].read()), encoding='utf8')
print("Reading tags from bucket --- done")

auth_provider = PlainTextAuthProvider(username=CASSANDRA_USER, password=CASSANDRA_PWD)
cluster = Cluster([CASSANDRA_HOST], auth_provider=auth_provider)
cassandrasession = cluster.connect(KEYSPACE)

insertlogs = cassandrasession.prepare("INSERT INTO tag (post_id, tag_token) VALUES (?, ?)")
counter = 0
totalcount = 0
batches = []
batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
print("Sending {} tags to cassandra".format(len(tagsdf)))

for index, values in tagsdf.iterrows():
    batch.add(insertlogs,
                (values['id'], values['tag']))
    counter += 1
    if counter >= BATCH_SIZE:
        print('Inserting ' + str(counter) + ' records from batch')
        totalcount += counter
        counter = 0
        rs = cassandrasession.execute(batch, trace=True)
        batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)

totalcount += counter
print('Inserted ' + str(totalcount) + ' rows in total')

print("Done sending tags to cassandra")
print("Bye Bye!")

