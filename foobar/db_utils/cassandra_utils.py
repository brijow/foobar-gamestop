import os

import pandas as pd
from cassandra.cluster import Cluster
from cassandra.query import dict_factory

CASSANDRA_HOST = (
    os.environ.get("CASSANDRA_HOST")
    if os.environ.get("CASSANDRA_HOST")
    else "localhost"
)
CASSANDRA_KEYSPACE = (
    os.environ.get("CASSANDRA_KEYSPACE")
    if os.environ.get("CASSANDRA_KEYSPACE")
    else "kafkapipeline"
)

GAMESTOP_TABLE = (
    os.environ.get("GAMESTOP_TABLE") if os.environ.get("GAMESTOP_TABLE") else "gamestop"
)
TAG_TABLE = os.environ.get("TAG_TABLE") if os.environ.get("TAG_TABLE") else "tag"
POST_TABLE = os.environ.get("POST_TABLE") if os.environ.get("POST_TABLE") else "post"
WIDE_TABLE = os.environ.get("WIDE_TABLE") if os.environ.get("WIDE_TABLE") else "wide"


def query_table(source_table):
    # source_table: target table name to query (string)
    if isinstance(CASSANDRA_HOST, list):
        cluster = Cluster(CASSANDRA_HOST)
    else:
        cluster = Cluster([CASSANDRA_HOST])

    if source_table not in (GAMESTOP_TABLE, TAG_TABLE, POST_TABLE, WIDE_TABLE):
        return None

    session = cluster.connect(CASSANDRA_KEYSPACE)
    session.row_factory = dict_factory

    cqlquery = f"SELECT * FROM {source_table};"
    rows = session.execute(cqlquery)
    return pd.DataFrame(rows)


# def query_all(source_table):
#     # source_table: target table name to query (string)

#      if isinstance(CASSANDRA_HOST, list):
#         cluster = Cluster(CASSANDRA_HOST)
#     else:
#         cluster = Cluster([CASSANDRA_HOST])

#     if source_table not in (GAMESTOP_TABLE, TAG_TABLE, POST_TABLE, WIDE_TABLE):
#         return None

#     if not isinstance(hour_from, datetime.date) or not isinstance(
#         hour_to, datetime.date
#     ):
#         return None

#     session = cluster.connect(CASSANDRA_KEYSPACE)
#     session.row_factory = dict_factory

#     cqlquery = f"SELECT type FROM system_schema.columns WHERE keyspace_name = {CASSANDRA_KEYSPACE} AND table_name = {source_table}"
#     column_types = session.execute(cqlquery)
#     timestamp_col = next((x for x in column_types if x=='TIMESTAMP'), 'timestamp_')

#     cqlquery = f"SELECT * FROM {source_table} WHERE  AND table_name = {source_table}"
