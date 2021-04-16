from datetime import datetime, timedelta

def get_posts_in_date_range_as_df(session, start_date=None, end_date=None):
    """Accepts two valid datetime.datetime objects"""

    start_date = start_date or datetime.now()
    end_date = end_date or start_date + timedelta(hours=1)

    start_date = start_date.strftime("%Y-%m-%d %H:00:00")
    end_date = end_date.strftime("%Y-%m-%d %H:00:00")

    cqlquery = f"SELECT * FROM post WHERE dt >= '{start_date}' AND dt < '{end_date}' ALLOW FILTERING;"
    rows = session.execute(cqlquery)
    return pd.DataFrame(rows)


def get_tags_in_post_id_list_as_df(session, post_id_list):
    """Accepts a list of post_id strings"""
    post_id_tuple = tuple(post_id_list)
    placeholders = ", ".join("%s" for i in post_id_tuple)
    cqlquery = f"SELECT * FROM tag WHERE post_id in ({placeholders})"
    rows = session.execute(cqlquery, post_id_tuple)
    return pd.DataFrame(rows)


def get_gamestop_in_date_range_as_df(session, start_date=None, end_date=None):
    """Accepts two valid datetime.datetime objects"""

    start_date = start_date or datetime.now()
    end_date = end_date or start_date + timedelta(hours=1)

    start_date = start_date.strftime("%Y-%m-%d %H:00:00")
    end_date = end_date.strftime("%Y-%m-%d %H:00:00")

    cqlquery = f"""
    SELECT * FROM gamestop
    WHERE timestamp_ >= '{start_date}'
    AND timestamp_ < '{end_date}' ALLOW FILTERING;
    """
    rows = session.execute(cqlquery)
    return pd.DataFrame(rows)


def join_posts_and_tags(session, start_date, end_date):
    joined_df = pd.DataFrame()

    posts_df = get_posts_in_date_range_as_df(session, start_date, end_date)
    if posts_df.empty: return joined_df

    post_id_list = posts_df['id'].tolist()
    tags_df = get_tags_in_post_id_list_as_df(session, post_id_list)
    if tags_df.empty: return joined_df

    joined_df = posts_df.set_index('id').join(tags_df.set_index('post_id'))
    return joined_df


def test_a_few_days(session):
    dti = pd.date_range("2021-02-01", periods=3, freq="H")
    for start_date in dti:
        end_date = start_date + timedelta(hours=1)
        df = join_posts_and_tags(session, start_date, end_date)
        if df.empty: continue

        all_sentiments = df[['positive', 'negative', 'neutral']].mean().fillna(0)
        all_sentiments = all_sentiments.rename({'positive': 'avg_all_post_pos',
                                                'negative': 'avg_all_post_neg',
                                                'neutral': 'avg_all_post_neu'})

        gme_df = df[df['tag_token'] == 'GME']
        gme_sentiments = gme_df[['positive', 'negative', 'neutral']].mean().fillna(0)
        gme_sentiments = gme_sentiments.rename({'positive': 'avg_gme_post_pos',
                                                'negative': 'avg_gme_post_neg',
                                                'neutral': 'avg_gme_post_neu'})

