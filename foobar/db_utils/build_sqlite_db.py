import os

import pandas as pd
from sqlalchemy import create_engine

from foobar.data_loader import get_root_data_dir, get_or_create_processed_data_dir
from foobar.db_utils.models import Base, Tag

data_dir = get_root_data_dir()


def _get_or_create_db_dir():
    """Return the path of the db dir."""
    db_dir = os.environ.get(
        "FOOBAR_SQLITE_DIR", os.path.join(get_root_data_dir(), "db")
    )
    dir_path = os.path.expanduser(db_dir)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


def create_gamestop_db(force_refresh=False):
    db_dir = _get_or_create_db_dir()
    file_path = os.path.join(db_dir, "gamestop.db")

    if os.path.exists(file_path) and force_refresh:
        os.remove(file_path)

    # if not os.path.exists(file_path):
    engine = create_engine(f"sqlite:///{file_path}")
    Base.metadata.create_all(engine)


def populate_posts_gamestop_db(limit_csvs=10):

    db_dir = _get_or_create_db_dir()
    file_path = os.path.join(db_dir, "gamestop.db")
    engine = create_engine(f"sqlite:///{file_path}")

    proc_dir = get_or_create_processed_data_dir()
    post_dir = os.path.join(proc_dir, "posts")

    for cnt, f in enumerate(os.scandir(post_dir)):
        if cnt > limit_csvs:
            print(f"Inserted {cnt} csv files to db")
            return

        if not (f.path.endswith(".csv") and f.is_file()):
            continue

        to_insert = pd.read_csv(f.path)
        to_insert = to_insert.drop("Unnamed: 0", axis=1)

        try:
            to_insert.to_sql(name="post", con=engine, if_exists="append", index=False)
            print("Successful insert!")
        except Exception as e:
            print("Initial failure to append: {}\n".format(e))
            print("Attempting to rectify...")
            existing = pd.read_sql("post", con=engine)
            mask = ~to_insert.id.isin(existing.id)
        try:
            to_insert.loc[mask].to_sql(
                name="post", con=engine, if_exists="append", index=False
            )
            print("Successful deduplication.")
        except Exception as e2:
            "Could not rectify duplicate entries. \n{}".format(e2)
        print("Success after dedupe")


def populate_tags_gamestop_db(limit_csvs=10):

    db_dir = _get_or_create_db_dir()
    file_path = os.path.join(db_dir, "gamestop.db")
    engine = create_engine(f"sqlite:///{file_path}")

    proc_dir = get_or_create_processed_data_dir()
    tag_dir = os.path.join(proc_dir, "tags")

    for cnt, f in enumerate(os.scandir(tag_dir)):
        if cnt > limit_csvs:
            print(f"Inserted {cnt} csv files to db")
            return

        if not (f.path.endswith(".csv") and f.is_file()):
            continue

        to_insert = pd.read_csv(f.path)
        to_insert = to_insert.drop("Unnamed: 0", axis=1)
        to_insert = to_insert.rename(columns={"tag": "token"})
        to_insert = to_insert.drop_duplicates()

        try:
            engine.execute(Tag.__table__.insert(), to_insert.to_dict("records"))
            print("Successful insert!")
        except Exception as e:
            print("Initial failure to append: {}\n".format(e))
            continue
