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
print("{} Starting Finnhub preloader".format(now.strftime("%Y-%m-%d %H:%M:%S")))

CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST") if os.environ.get("CASSANDRA_HOST") else "localhost"
CASSANDRA_USER = os.environ.get("CASSANDRA_USER")
CASSANDRA_PWD = os.environ.get("CASSANDRA_PWD")
KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE") if os.environ.get("CASSANDRA_KEYSPACE") else 'kafkapipeline'
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 100))
NUM_WORKERS = int(os.environ.get("NUM_WORKERS", 10))

os.environ['AWS_ACCESS_KEY_ID'] = 'AKIA3FK2NHCARLS3RA7X'
os.environ['AWS_SECRET_KEY'] = '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'
os.environ['REGION_NAME'] = 'us-west-2'

GAMESTOP_TABLE = (
    os.environ.get("GAMESTOP_TABLE") if os.environ.get("GAMESTOP_TABLE") else "gamestop"
)

BUCKET_NAME = (
    os.environ.get("BUCKET_NAME")
    if os.environ.get("BUCKET_NAME")
    else "bb-s3-bucket-cmpt733"
)

session = boto3.Session(
                    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=os.environ['AWS_SECRET_KEY'],
                    region_name=os.environ['REGION_NAME'])
                    
s3 = session.resource('s3')
bucket = s3.Bucket(BUCKET_NAME)
print("Reading data from bucket")
postsobj = bucket.Object(key='gme.csv')
response = postsobj.get()
historicaldata = pd.read_csv(io.BytesIO(response['Body'].read()), encoding='utf8')
historicaldata['hour'] = pd.to_datetime(historicaldata['hour'])

historicaldata = historicaldata.rename(
                columns={
                    "closeprice": "close_price",
                    "openprice": "open_price",
                    "highprice": "high_price",
                    "lowprice": "low_price",
                }
            )
historicaldata = historicaldata.drop("prediction", axis=1)
print("Reading data from bucket --- done")
print("Splitting data")
databatches = np.array_split(historicaldata, 100)

auth_provider = PlainTextAuthProvider(username=CASSANDRA_USER, password=CASSANDRA_PWD)
cluster = Cluster([CASSANDRA_HOST], auth_provider=auth_provider)
# cluster = Cluster([CASSANDRA_HOST])
cassandrasession = cluster.connect(KEYSPACE)

insertlogs = cassandrasession.prepare(f"INSERT INTO {GAMESTOP_TABLE} (hour, \
                                    open_price, high_price, \
                                    low_price, volume, close_price) \
                                    VALUES (?, ?, ?, ?, ?, ?)")

counter = 0
totalcount = 0
batches = []
now = datetime.datetime.now()
print("{} Sending {} data to cassandra in {} batches with {} rows"\
    .format(now.strftime("%Y-%m-%d %H:%M:%S"), len(historicaldata), \
        len(databatches), len(databatches[0])))

with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
    for df_ in databatches:
        def processit(df):
            counter = 0
            batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
            for index, values in df.iterrows():
                batch.add(insertlogs,
                    (values['hour'], values['open_price'], values['high_price'], 
                    values['low_price'], values['volume'], values['close_price']))
                counter += 1
                if counter >= BATCH_SIZE:
                    # print('Inserting ' + str(counter) + ' records from batch')
                    counter = 0
                    cassandrasession.execute(batch, trace=True)
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
print("{} Done sending finnhub data to cassandra".format(now.strftime("%Y-%m-%d %H:%M:%S")))
print("Bye Bye!")