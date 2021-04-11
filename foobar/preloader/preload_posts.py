import io
import sys
import os
from cassandra.cluster import Cluster, BatchStatement, ConsistencyLevel, uuid
from cassandra.auth import PlainTextAuthProvider
import boto3
import pandas as pd
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import datetime

print("Starting Reddit posts preloader")

CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST")
CASSANDRA_USER = os.environ.get("CASSANDRA_USER")
CASSANDRA_PWD = os.environ.get("CASSANDRA_PWD")
KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 100))
NUM_WORKERS = int(os.environ.get("NUM_WORKERS", 10))

session = boto3.Session(
                    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=os.environ['AWS_SECRET_KEY'],
                    region_name=os.environ['REGION_NAME'])
                    
s3 = session.resource('s3')
bucket = s3.Bucket(BUCKET_NAME)
print("Reading posts from bucket")
postsobj = bucket.Object(key='posts.csv')
response = postsobj.get()
postsdf = pd.read_csv(io.BytesIO(response['Body'].read()), encoding='utf8')
postsdf['dt'] = pd.to_datetime(postsdf['dt'])
posts = np.array_split(postsdf, 100)
print("Reading posts from bucket --- done")

auth_provider = PlainTextAuthProvider(username=CASSANDRA_USER, password=CASSANDRA_PWD)
cluster = Cluster([CASSANDRA_HOST], auth_provider=auth_provider)
cassandrasession = cluster.connect(KEYSPACE)

insertlogs = cassandrasession.prepare("INSERT INTO post (id, iscomment, submission_id, parent_id, \
                                    username, positive, negative, neutral, dt) \
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")
counter = 0
totalcount = 0
batches = []
now = datetime.datetime.now()
print("{} Sending {} posts to cassandra in {} batches with {} rows".format(now.strftime("%Y-%m-%d %H:%M:%S"), len(postsdf), len(posts), len(posts[0])))

with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
    for df_ in posts:
        def processit(df):
            counter = 0
            batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
            for index, values in df.iterrows():
                batch.add(insertlogs,
                    (values['id'], values['iscomment'], values['submission_id'], values['parent_id'], 
                    values['user'], values['positive'], values['negative'], values['neutral'], values['dt']))
                counter += 1
                if counter >= BATCH_SIZE:
                    # print('Inserting ' + str(counter) + ' records from batch')
                    counter = 0
                    try:
                        cassandrasession.execute(batch, trace=True)
                    except Exception as exc:
                        print(f"Exception {exc}")
                        cassandrasession.execute(batch, trace=True)
                        print("Successfully recovered")
                    batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
            if counter > 0:
                cassandrasession.execute(batch, trace=True)
            return len(df)
        exec_ = lambda : processit(df_)
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
now = datetime.datetime.now()
print("{} Done sending posts to cassandra".format(now.strftime("%Y-%m-%d %H:%M:%S")))
print("Bye Bye!")