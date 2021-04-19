import io
import sys
import os
from cassandra.cluster import Cluster, BatchStatement, ConsistencyLevel, uuid
from cassandra.auth import PlainTextAuthProvider
import boto3
import pandas as pd
import zipfile
import numpy as np
import datetime
import time

now = datetime.datetime.now()
print("{} Starting Wide table preloader".format(now.strftime("%Y-%m-%d %H:%M:%S")))

CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST") if os.environ.get("CASSANDRA_HOST") else "localhost"
CASSANDRA_USER = os.environ.get("CASSANDRA_USER")
CASSANDRA_PWD = os.environ.get("CASSANDRA_PWD")
CASSANDRA_KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE") if os.environ.get("CASSANDRA_KEYSPACE") else "kafkapipeline"

BUCKET_NAME = (
    os.environ.get("BUCKET_NAME")
    if os.environ.get("BUCKET_NAME")
    else "bb-s3-bucket-cmpt733"
)
TABLE_NAME = (
    os.environ.get("TABLE_NAME") if os.environ.get("TABLE_NAME") else "wide"
)
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 200))
NUM_WORKERS = int(os.environ.get("NUM_WORKERS", 10))


session = boto3.Session(
                    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=os.environ['AWS_SECRET_KEY'],
                    region_name=os.environ['REGION_NAME'])
                    
s3 = session.resource('s3')
bucket = s3.Bucket(BUCKET_NAME)
print("Reading records from bucket")
postsobj = bucket.Object(key='wide.csv')
response = postsobj.get()
wide_df = pd.read_csv(io.BytesIO(response['Body'].read()), encoding='utf8')
# wide_df['hour'] = pd.to_datetime(wide_df['hour'])
wide_df['hour'] = pd.to_datetime(wide_df['hour'], format='%Y-%m-%d %H:%M:%S')
records = np.array_split(wide_df, 100)

now = datetime.datetime.now()
print("{} Reading records from bucket --- done".format(now.strftime("%Y-%m-%d %H:%M:%S")))

auth_provider = PlainTextAuthProvider(username=CASSANDRA_USER, password=CASSANDRA_PWD)
cluster = Cluster([CASSANDRA_HOST], auth_provider=auth_provider)
# cluster = Cluster([CASSANDRA_HOST])

counter = 0
totalcount = 0
batches = []
now = datetime.datetime.now()
print("{} Sending {} records to cassandra in {} batches with {} rows".format(now.strftime("%Y-%m-%d %H:%M:%S"), len(wide_df), len(records), len(records[0])))

cassandrasession = cluster.connect(CASSANDRA_KEYSPACE)
cassandrasession.default_timeout = 60
cassandrasession.request_timeout = 30

for df_ in records:
    def processit(df):

        
        insertlogs = cassandrasession.prepare("INSERT INTO wide (hour, avg_all_post_pos, \
                                            avg_all_post_neg, avg_all_post_neu, \
                                            cnt_all_user, cnt_all_tag, cnt_all_post, cnt_all_comments, \
                                            avg_gme_post_pos, avg_gme_post_neg, avg_gme_post_neu, \
                                            cnt_gme_user, cnt_gme_tag, cnt_gme_post, \
                                            cnt_gme_comments, volume, open_price, \
                                            close_price, high_price, low_price, \
                                            prediction_finn, prediction_wide, prediction_reddit) \
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, \
                                                    ?, ?, ?, ?, ?, ?)")
        counter = 0
        batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)
        for index, values in df.iterrows():
            batch.add(insertlogs,
                (values['hour'], values['avg_all_post_pos'], values['avg_all_post_neg'], values['avg_all_post_neu'], 
                    values['cnt_all_user'], values['cnt_all_tag'], values['cnt_all_post'], values['cnt_all_comments'],
                    values['avg_gme_post_pos'], values['avg_gme_post_neg'], values['avg_gme_post_neu'],
                    values['cnt_gme_user'], values['cnt_gme_tag'], values['cnt_gme_post'], values['cnt_gme_comments'],
                    values['volume'], values['open_price'], values['close_price'], values['high_price'],
                    values['low_price'], values['prediction_finn'], values['prediction_wide'], values['prediction_reddit']))
            counter += 1
            if counter >= BATCH_SIZE:
                counter = 0
                try:
                    cassandrasession.execute(batch, trace=True)
                except Exception as exc:
                    print(f"Exception {exc}")
                    try:
                        cassandrasession.execute(batch, trace=True)
                    except Exception as exc:
                        print(f"2nd Exception {exc}")

                batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)
        if counter > 0:
            cassandrasession.execute(batch, trace=True)
        return len(df)
    totalcount += processit(df_)
    # batches.append(executor.submit(exec_))
    # print("Waiting batches to process...")

now = datetime.datetime.now()
print("{} Done sending {} records to cassandra".format(now.strftime("%Y-%m-%d %H:%M:%S"), totalcount))

def query_table(source_table, colstring="*"):
    # source_table: target table name to query (string)
    auth_provider = PlainTextAuthProvider(username=CASSANDRA_USER, password=CASSANDRA_PWD)
    cluster = Cluster([CASSANDRA_HOST], auth_provider=auth_provider)
    session = cluster.connect(CASSANDRA_KEYSPACE)
    # session.row_factory = dict_factory
    cqlquery = f"SELECT {colstring} FROM {source_table};"
    rows = session.execute(cqlquery)
    return pd.DataFrame(rows)

foundrows = query_table(TABLE_NAME)
print(f"Inserted {len(foundrows)} rows in total")
print("Bye Bye!")
time.sleep(10) #adding sleep here just to be able to see the logs after running.