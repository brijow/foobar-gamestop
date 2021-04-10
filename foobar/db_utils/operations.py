import os

import pandas as pd

from foobar.data_loader import get_root_data_dir, get_or_create_processed_data_dir

from importlib import resources

from sqlalchemy import and_, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import asc, desc, func
from treelib import Tree

from foobar.db_utils.models import Base, Gamestop, Post, Tag


def connect_to_db():
    db_dir = os.path.join(os.environ.get(
        "FOOBAR_SQLITE_DIR"), "db")
    file_path = os.path.join(db_dir, "gamestop.db")
    if not os.path.isfile(file_path):
        print("Oops")
        return None
    engine = create_engine(f"sqlite:///{file_path}")
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    return session

def get_post_minmax_dates(session):
    return session.query(
        func.max(Post.dt).label("end_date"), 
        func.min(Post.dt).label("start_date")
    ).one()

def get_posts_by_day(session, day1):
    day2 = day1 + pd.DateOffset(1)
    return session.query(Post).filter(
            Post.dt >= day1.to_pydatetime(), 
            Post.dt < day2.to_pydatetime()
        ).all()

def get_tags_for_postids(session, postids):
    return session.query(Tag).filter(Tag.post_id.in_(postids)).all()

# def get_post_ids_for_tag(session, target_tags):
#     return session.query(Tag).filter(Tag.token.in_(target_tags)).all()

def join_post_tag_db_v2(session, day1):
    day2 = day1 + pd.DateOffset(1)
    return session.query(
            Post.id, Post.iscomment, Post.submission_id,
            Post.positive, Post.negative, Post.neutral,
            Post.user, Post.dt, Tag.tag
        ).filter(
            Post.dt >= day1.to_pydatetime(), 
            Post.dt < day2.to_pydatetime(),
            Post.id == Tag.post_id).all()


# def join_post_tag_db(session):
#     return session.query(
#             Post.id, Post.iscomment, Post.submission_id,
#             Post.positive, Post.negative, Post.neutral,
#             Post.user, Post.dt, Tag.token
#         ).filter(Post.id == Tag.post_id).all()

def join_post_tag_df(df_tag, df_posts):
    df = df_posts.merge(df.join, how='left', left_on='id', right_on='post_id')
    df = df[[
        'id', 'iscomment', 'submission_id',
        'positive', 'negative', 'neutral', 'user', 'dt', 'tag'
    ]]
    return df

def round_to_hour(df, dt_col):
    df['hour'] = df[dt_col].dt.floor('H')
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

def fill_missing_hours(df, running_date):
    last_hour = running_date + pd.DateOffset(hours=23)
    all_hours = pd.date_range(running_date, last_hour, freq='H').to_frame()
    new = all_hours.merge(df, right_on="hour", left_index=True, how='left')
    new = new.drop(columns='hour')
    new = new.rename(columns={0:'hour'})
    return new


def make_reddit_hourly(running_date):
    df = pd.DataFrame.from_records(join_post_tag_db_v2(s, i))
    df.columns = [
        'id', 'iscomment', 'submission_id',
        'positive', 'negative', 'neutral', 'user', 'dt', 'tag'
    ]

    df = round_to_hour(df, 'dt')
    df_all = get_aggregates_by_hour(df)

    df_gme = df[(df['tag'] == "GME") | (df['tag'] == "GAMESTOP")]
    df_gme = get_aggregates_by_hour(df_gme)

    final = df_all.merge(df_gme, left_on="hour", right_on="hour", how='left', suffixes=('_all', '_gme'))    
    final = fill_missing_hours(final, running_date).fillna(0)
    return final


def make_financial_hourly(session, day1):
    day2 = day1 + pd.DateOffset(1)

    return session.query(Gamestop).filter(
            Gamestop.hour >= day1.to_pydatetime(), 
            Gamestop.hour < day2.to_pydatetime()
        ).all()

def build_wide_table(df_reddit, df_financial):
    # df = pd.DataFrame.from_records(join_post_tag_db(session))
    # df.columns = [
    #     'id', 'iscomment', 'submission_id',
    #     'positive', 'negative', 'neutral', 'user', 'dt', 'token'
    # ]

    # df = join_post_tag_df(df_tag, df_posts)

    df = df_reddit.join(df_financial, on='hour', lsuffix='_1', rsuffix='_2')

    df = df.drop(columns=['hour_2'])
 
    df.columns = ['hour', 'avg_all_post_pos', 'avg_all_post_neg', 'avg_all_post_neu',
    'cnt_all_user', 'cnt_all_tag', 'cnt_all_post', 'cnt_all_comments', 'avg_gme_post_pos',
    'avg_gme_post_neg', 'avg_gme_post_neu', 'cnt_gme_user', 'cnt_gme_tag', 'cnt_gme_post',
    'cnt_gme_comments', 'id', 'openprice', 'lowprice', 'highprice', 'volume', 'closeprice',
    'prediction']
    col = df.pop("id")
    df.insert(0, col.name, col)
    return df


if __name__ == "__main__":
    s = connect_to_db()
    result = get_post_minmax_dates(s)
    start_date = result.start_date.replace(minute=0, hour=0, second=0, microsecond=0)
    end_date = result.end_date.replace(minute=0, hour=0, second=0, microsecond=0)
    post_cols = [c.name for c in Post.__table__.columns]
    tag_cols = [c.name for c in Tag.__table__.columns]
    gamestop_cols = [c.name for c in Gamestop.__table__.columns]
    full_wide = pd.DataFrame()
    # proc_dir = get_or_create_processed_data_dir()
    # wide_csv = os.path.join(proc_dir, "wide.csv")
    wide_csv = "wide.csv"
    c = 0
    for i in pd.date_range(start_date, end_date, freq='D'): 
        if c < 8:
            c += 1
            continue       
        # tuplefied_posts = [(getattr(item, col) for col in post_cols) for item in get_posts_by_day(s, i)]
        # df_daily_posts = pd.DataFrame.from_records(tuplefied_posts, columns=post_cols)

        # tuplefied_tags = [(getattr(item, col) for col in tag_cols) for item in get_tags_for_postids(s, df_daily_posts['id'].tolist())]
        # df_daily_tags = pd.DataFrame.from_records(tuplefied_tags, columns=tag_cols)
        # build_wide_table(df_daily_posts, df_daily_tags, i)

        df_reddit = make_reddit_hourly(i)
        tuplefied_finance = [(getattr(item, col) for col in gamestop_cols) for item in make_financial_hourly(s, i)]
        if not tuplefied_finance:
            print("Market closed for the day", str(i))
            continue
        df_financial = pd.DataFrame.from_records(tuplefied_finance, columns=gamestop_cols)
        print(df_financial)
        df_financial = fill_missing_hours(df_financial, i).ffill().bfill() # Should I be doing this for missing data???
        
        df_wide = build_wide_table(df_reddit, df_financial)
        
        if not os.path.isfile(wide_csv):
            df_wide.to_csv(wide_csv)
        else: # else it exists so append without writing the header
            df_wide.to_csv(wide_csv, mode='a', header=False)


    # build_wide_table(s)
    # proc_dir = get_or_create_processed_data_dir()
    # post_dir = os.path.join(proc_dir, "posts")
    # df_posts = read_csvs(post_dir)

    # tag_dir = os.path.join(proc_dir, "tags")
    # df_tag = read_csvs(tag_dir)
    # wide_df = build_wide_table(df_tag, df_posts)


