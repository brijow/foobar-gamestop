import io
import os
import sys
import datetime
from cassandra.cluster import Cluster, BatchStatement, ConsistencyLevel, uuid
from cassandra.auth import PlainTextAuthProvider
import boto3
import pandas as pd
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

print("Starting Reddit tags preloader")

CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST")
CASSANDRA_USER = os.environ.get("CASSANDRA_USER")
CASSANDRA_PWD = os.environ.get("CASSANDRA_PWD")
KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
BATCH_SIZE = int(os.environ.get("BATCH_SIZE"))
NUM_WORKERS = int(os.environ.get("NUM_WORKERS", 25))

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
tags = np.array_split(tagsdf, 100)
print("Reading tags from bucket --- done")

auth_provider = PlainTextAuthProvider(username=CASSANDRA_USER, password=CASSANDRA_PWD)
cluster = Cluster([CASSANDRA_HOST], auth_provider=auth_provider)
cassandrasession = cluster.connect(KEYSPACE)

insertlogs = cassandrasession.prepare("INSERT INTO tag (id, post_id, tag_token) VALUES (?, ?, ?)")

totalcount = 0
batches = []
now = datetime.datetime.now()
print("{} Sending {} tags to cassandra in {} batches with {} rows".format(now.strftime("%Y-%m-%d %H:%M:%S"), len(tagsdf), len(tags), len(tags[0])))

with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
    for tagsdf_ in tags:
        def processit(df):
            counter = 0
            batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
            for index, values in df.iterrows():
                batch.add(insertlogs,
                            (str(uuid.uuid4()), values['id'], values['tag']))
                counter += 1
                if counter >= BATCH_SIZE:
                    # print('Inserting ' + str(counter) + ' records from batch')
                    counter = 0
                    cassandrasession.execute(batch, trace=True)
                    batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
            if counter > 0:
                cassandrasession.execute(batch, trace=True)
            return len(df)
        exec_ = lambda : processit(tagsdf_)
        batches.append(executor.submit(exec_))
    print("Waiting batches to process...")
    finishedjobs = 0
    for future in as_completed(batches):
        try:
            data = future.result()
            totalcount += data
        except Exception as exc:
            print('Exception: %s' % (exc))

print('Inserted ' + str(totalcount) + ' rows in total')
print("Finished rows: {}".format(finishedjobs))
now = datetime.datetime.now()
print("{} Done sending tags to cassandra".format(now.strftime("%Y-%m-%d %H:%M:%S")))
print("Bye Bye!")

