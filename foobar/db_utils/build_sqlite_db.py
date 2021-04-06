import os

from sqlalchemy import create_engine

from foobar.data_loader import get_root_data_dir
from foobar.db_utils.models import Base

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
