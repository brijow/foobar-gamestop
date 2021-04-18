"""Methods defined in this file return records as rows in pandas dataframes"""

from datetime import datetime, timedelta
import pandas as pd


def select_posts_by_hour_range(session, start_date=None, end_date=None):
    """Accepts two valid datetime.datetime objects"""

    start_date = start_date or datetime.now()
    end_date = end_date or start_date + timedelta(hours=1)

    start_date = start_date.strftime("%Y-%m-%d %H:00:00")
    end_date = end_date.strftime("%Y-%m-%d %H:00:00")

    cqlquery = f"SELECT * FROM post WHERE dt >= '{start_date}' AND dt < '{end_date}' ALLOW FILTERING;"
    rows = session.execute(cqlquery)
    found = pd.DataFrame(rows)
    if not found.empty:
        found = found.rename(
                    columns={
                        "dt": "hour",
                    }
                )
    return found


def select_tags_by_postids(session, post_id_list):
    """Accepts a list of post_id strings"""
    post_id_tuple = tuple(post_id_list)
    placeholders = ", ".join("%s" for i in post_id_tuple)
    cqlquery = f"SELECT * FROM tag WHERE post_id in ({placeholders})"
    rows = session.execute(cqlquery, post_id_tuple)
    return pd.DataFrame(rows)


def select_gamestops_by_hour_range(session, start_date=None, end_date=None):
    """Accepts two valid datetime.datetime objects"""

    start_date = start_date or datetime.now()
    end_date = end_date or start_date + timedelta(hours=1)

    start_date = start_date.strftime("%Y-%m-%d %H:00:00")
    end_date = end_date.strftime("%Y-%m-%d %H:00:00")

    cqlquery = f"""
    SELECT * FROM gamestop
    WHERE hour >= '{start_date}'
    AND hour < '{end_date}' ALLOW FILTERING;
    """
    rows = session.execute(cqlquery)
    return pd.DataFrame(rows)


def select_all_from_wide_table(session):
    cqlquery = "SELECT * FROM wide;"
    rows = session.execute(cqlquery)
    return pd.DataFrame(rows)
