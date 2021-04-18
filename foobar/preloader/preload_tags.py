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

CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST") if os.environ.get("CASSANDRA_HOST") else "localhost"
CASSANDRA_USER = os.environ.get("CASSANDRA_USER")
CASSANDRA_PWD = os.environ.get("CASSANDRA_PWD")
CASSANDRA_KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE") if os.environ.get("CASSANDRA_KEYSPACE") else 'kafkapipeline'
BUCKET_NAME = (
    os.environ.get("BUCKET_NAME")
    if os.environ.get("BUCKET_NAME")
    else "bb-s3-bucket-cmpt733"
)
BATCH_SIZE = int(os.environ.get("BATCH_SIZE"))
NUM_WORKERS = int(os.environ.get("NUM_WORKERS", 25))
TABLE_NAME = (
    os.environ.get("TABLE_NAME") if os.environ.get("TABLE_NAME") else "tag"
)
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIA3FK2NHCARLS3RA7X'
os.environ['AWS_SECRET_KEY'] = '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'
os.environ['REGION_NAME'] = 'us-west-2'

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


totalcount = 0
batches = []
now = datetime.datetime.now()
print("{} Sending {} tags to cassandra in {} batches with {} rows"\
    .format(now.strftime("%Y-%m-%d %H:%M:%S"), len(tagsdf), len(tags), len(tags[0])))

with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
    for tagsdf_ in tags:
        def processit(df):
            cassandrasession = cluster.connect(CASSANDRA_KEYSPACE)
            cassandrasession.default_timeout = 60
            cassandrasession.request_timeout = 30
            insertlogs = cassandrasession.prepare(f"INSERT INTO {TABLE_NAME} \
                (id, post_id, tag_token) VALUES (?, ?, ?)")
            counter = 0
            batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)
            for index, values in df.iterrows():
                batch.add(insertlogs,
                            (str(uuid.uuid4()), values['post_id'], values['tag']))
                counter += 1
                if counter >= BATCH_SIZE:
                    # print('Inserting ' + str(counter) + ' records from batch')
                    counter = 0
                    cassandrasession.execute(batch, trace=True)
                    batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)
            if counter > 0:
                cassandrasession.execute(batch, trace=True)
            return len(df)
        exec_ = lambda : processit(tagsdf_)
        batches.append(executor.submit(exec_))
    print("Waiting batches to process...")
    for future in as_completed(batches):
        try:
            data = future.result()
            totalcount += data
        except Exception as exc:
            print('Exception: %s' % (exc))

now = datetime.datetime.now()
print("{} Done sending tags to cassandra".format(now.strftime("%Y-%m-%d %H:%M:%S")))

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

