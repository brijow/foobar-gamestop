import io
import sys
import os
from cassandra.cluster import Cluster, BatchStatement, ConsistencyLevel
from cassandra.auth import PlainTextAuthProvider
import boto3
import pandas as pd
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import datetime

now = datetime.datetime.now()
print("{} Starting Reddit posts preloader".format(now.strftime("%Y-%m-%d %H:%M:%S")))

CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST") if os.environ.get("CASSANDRA_HOST") else "localhost"
CASSANDRA_USER = os.environ.get("CASSANDRA_USER")
CASSANDRA_PWD = os.environ.get("CASSANDRA_PWD")
CASSANDRA_KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE") if os.environ.get("CASSANDRA_KEYSPACE") else 'kafkapipeline'
BUCKET_NAME = (
    os.environ.get("BUCKET_NAME")
    if os.environ.get("BUCKET_NAME")
    else "bb-s3-bucket-cmpt733"
)
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 100))
NUM_WORKERS = int(os.environ.get("NUM_WORKERS", 10))
TABLE_NAME = (
    os.environ.get("TABLE_NAME") if os.environ.get("TABLE_NAME") else "post"
)
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

counter = 0
totalcount = 0
batches = []
now = datetime.datetime.now()
print("{} Sending {} posts to cassandra in {} batches with {} rows".format(now.strftime("%Y-%m-%d %H:%M:%S"), 
                                                                            len(postsdf), len(posts), len(posts[0])))

with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
    for df_ in posts:
        def processit(df):
            cassandrasession = cluster.connect(CASSANDRA_KEYSPACE)
            cassandrasession.default_timeout = 60
            cassandrasession.request_timeout = 30

            insertlogs = cassandrasession.prepare(f"INSERT INTO {TABLE_NAME} (id, iscomment, submission_id, parent_id, \
                                                username, positive, negative, neutral, dt) \
                                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")
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
                        try:
                            cassandrasession.execute(batch, trace=True)
                        except Exception as exc:
                            print(f"2nd Exception {exc}")

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
now = datetime.datetime.now()
print("{} Done sending posts to cassandra".format(now.strftime("%Y-%m-%d %H:%M:%S")))

def query_table(source_table, colstring="*"):
    
    auth_provider = PlainTextAuthProvider(username=CASSANDRA_USER, password=CASSANDRA_PWD)
    cluster = Cluster([CASSANDRA_HOST], auth_provider=auth_provider)

    session = cluster.connect(CASSANDRA_KEYSPACE)
    cqlquery = f"SELECT {colstring} FROM {source_table};"
    rows = session.execute(cqlquery)
    return pd.DataFrame(rows)

foundrows = query_table(TABLE_NAME)
now = datetime.datetime.now()
print("{} Inserted {} rows in total".format(now.strftime("%Y-%m-%d %H:%M:%S"), len(foundrows)))

print("Bye Bye!")