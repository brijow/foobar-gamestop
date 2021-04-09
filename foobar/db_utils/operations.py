import os

import pandas as pd

from foobar.data_loader import get_root_data_dir, get_or_create_processed_data_dir

# from importlib import resources

# from sqlalchemy import and_, create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.sql import asc, desc, func
# from treelib import Tree

# from foobar.db_utils.models import Tag, Post


# def connect_to_db():
#     db_dir = os.path.join(os.environ.get(
#         "FOOBAR_SQLITE_DIR"), "db")
#     file_path = os.path.join(db_dir, "gamestop.db")
#     if not os.path.isfile(file_path):
#         print("Oops")
#         return None

#     engine = create_engine(f"sqlite:///{file_path}")
#     Session = sessionmaker()
#     Session.configure(bind=engine)
#     session = Session()
#     return session

# def get_post_ids_for_tag(session, target_tags):
#     return session.query(Tag).filter(Tag.token.in_(target_tags)).all()

# def join_post_tag(session):
#     return session.query(
#             Post.id, Post.iscomment, Post.submission_id,
#             Post.positive, Post.negative, Post.neutral,
#             Post.user, Post.dt, Tag.token
#         ).filter(Post.id == Tag.post_id).all()

def join_post_tag(df_tag, df_posts):
    df = df_posts.merge(df.join, how='left', left_on='id', right_on='post_id')
    df = df[[
        'id', 'iscomment', 'submission_id',
        'positive', 'negative', 'neutral', 'user', 'dt', 'tag'
    ]]
    return df

def round_to_hour(df, dt_col):
    df['hour'] = df[dt_col].dt.round('H')
    return df

def get_aggregates_by_hour(df):
    grouped_df = df.groupby('hour')
    result = grouped_df.mean(['positive', 'negative', 'neutral'])
    result['User_count'] = grouped_df.agg({"user": "nunique"})
    result['Tag_count'] = grouped_df.agg({"tag": "nunique"})
    result['Total_count'] = grouped_df.size()
    result['Comments_count'] = grouped_df['iscomment'].sum().astype(int)
    result = result.drop(columns=['iscomment'], axis =1).reset_index()
    return result

def read_csvs(csvs_dir):
    big_df = pd.DataFrame()
    for cnt, f in enumerate(os.scandir(csvs_dir)):
        # if cnt > limit_csvs:
        #     print(f"Inserted {cnt} csv files to db")
        #     return

        if not (f.path.endswith(".csv") and f.is_file()):
            continue

        new_read = pd.read_csv(f.path)
        new_read = new_read.drop("Unnamed: 0", axis=1)
        big_df = pd.concat([big_df, new_read], ignore_index=True)
    return big_df

def build_wide_table(df_tag, df_posts):

    # df = pd.DataFrame.from_records(join_post_tag(session))
    # df.columns = [
    #     'id', 'iscomment', 'submission_id',
    #     'positive', 'negative', 'neutral', 'user', 'dt', 'token'
    # ]

    df = join_post_tag(df_tag, df_posts)

    df = round_to_hour(df, 'dt')
    df_all = get_aggregates_by_hour(df)

    df_gme = df[(df['tag'] == "GME") | (df['tag'] == "GAMESTOP")]
    df_gme = get_aggregates_by_hour(df_gme)
    
    final = df_all.merge(df_gme, left_on="hour", right_on="hour", how='outer', suffixes=('_all', '_gme'))
    # merge financial data here

    final = final.fillna(0)

    print(final.sample(20))
    print(final.describe())
    final = final.drop(columns=['Tag_count_gme'])

    return final


if __name__ = "__main__":
    # s = connect_to_db()
    # build_wide_table(s)
    proc_dir = get_or_create_processed_data_dir()
    post_dir = os.path.join(proc_dir, "posts")
    df_posts = read_csvs(post_dir)

    tag_dir = os.path.join(proc_dir, "tags")
    df_tag = read_csvs(tag_dir)
    wide_df = build_wide_table(df_tag, df_posts)


