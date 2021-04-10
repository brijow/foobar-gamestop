import io
import sys
import os
from cassandra.cluster import Cluster, BatchStatement, ConsistencyLevel, uuid
from cassandra.auth import PlainTextAuthProvider
import boto3
import pandas as pd
import zipfile

print("Starting Finnhub preloader")

CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST")
CASSANDRA_USER = os.environ.get("CASSANDRA_USER")
CASSANDRA_PWD = os.environ.get("CASSANDRA_PWD")
KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 100))

session = boto3.Session(
                    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=os.environ['AWS_SECRET_KEY'],
                    region_name=os.environ['REGION_NAME'])
                    
s3 = session.resource('s3')
bucket = s3.Bucket(BUCKET_NAME)
print("Reading data from bucket")
postsobj = bucket.Object(key='gme.csv')
response = postsobj.get()
postsdf = pd.read_csv(io.BytesIO(response['Body'].read()), encoding='utf8')
postsdf['hour'] = pd.to_datetime(postsdf['hour'])
print("Reading data from bucket --- done")

auth_provider = PlainTextAuthProvider(username=CASSANDRA_USER, password=CASSANDRA_PWD)
cluster = Cluster([CASSANDRA_HOST], auth_provider=auth_provider)
cassandrasession = cluster.connect(KEYSPACE)

insertlogs = cassandrasession.prepare("INSERT INTO gamestop (id, timestamp_, open_price, high_price, \
                                    low_price, volume, close_price) \
                                    VALUES (?, ?, ?, ?, ?, ?, ?)")

counter = 0
totalcount = 0
batches = []
batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
print("Sending {} data to cassandra".format(len(postsdf)))

for index, values in postsdf.iterrows():
    batch.add(insertlogs,
                (str(uuid.uuid4()), values['hour'], values['openprice'], values['highprice'], 
                values['lowprice'], values['volume'], values['closeprice']))

    counter += 1
    if counter >= BATCH_SIZE:
        # print('Inserting ' + str(counter) + ' records from batch')
        totalcount += counter
        counter = 0
        rs = cassandrasession.execute(batch, trace=True)
        batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)

totalcount += counter
print('Inserted ' + str(totalcount) + ' rows in total')

print("Done sending finnancial data to cassandra")
print("Bye Bye!")