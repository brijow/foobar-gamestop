import os

import pandas as pd
from importlib import resources

from sqlalchemy import and_, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import asc, desc, func
from treelib import Tree

# from foobar.data_loader import get_root_data_dir
# from foobar.db_utils.models import Tag, Post

# Replacing imports for now
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Float,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import backref, relationship

Base: DeclarativeMeta = declarative_base()

class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String)
    post_id = Column(Integer, ForeignKey("post.id"))
    __table_args__ = (UniqueConstraint("token", "post_id", name="_token_post_uc"),)

class Post(Base):
    __tablename__ = "post"
    id = Column(String, primary_key=True)
    submission_id = Column(String)
    iscomment = Column(Boolean)
    positive = Column(Float)
    negative = Column(Float)
    neutral = Column(Float)
    user = Column(String)
    dt = Column(DateTime)

    parent_id = Column(String, ForeignKey("post.id"), index=True)
    sub_posts = relationship("Post", backref=backref("parent", remote_side=[id]))

    tags = relationship("Tag", backref=backref("post"))


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

def get_post_ids_for_tag(session, target_tags):
    return session.query(Tag).filter(Tag.token.in_(target_tags)).all()

def join_post_tag(session):
    return session.query(
            Post.id, Post.iscomment, Post.submission_id,
            Post.positive, Post.negative, Post.neutral,
            Post.user, Post.dt, Tag.token
        ).filter(Post.id == Tag.post_id).all()

def by_the_hour(df, dt_col):
    df['hour'] = df[dt_col].dt.round('H')
    return df

def build_wide_table(session):

    df = pd.DataFrame.from_records(join_post_tag(session))
    df.columns = [
        'id', 'iscomment', 'submission_id',
        'positive', 'negative', 'neutral', 'user', 'dt', 'token'
    ]
    df = by_the_hour(df, 'dt')

    grouped_df = df.groupby(['hour', 'token'])

    computed = grouped_df.mean(['positive', 'negative', 'neutral'])
    computed['Total_count'] = grouped_df.size()
    computed['Comments_count'] = grouped_df['iscomment'].sum().astype(int)
    computed = computed.drop(columns=['iscomment'], axis =1).reset_index()

    # check = computed[computed['Total_count'] != computed['Comments_count']]
    # check = df[df['iscomment'] == False]
    print(computed)



s = connect_to_db()
build_wide_table(s)


