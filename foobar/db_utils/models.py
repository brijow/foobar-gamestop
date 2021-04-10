from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import backref, relationship

Base: DeclarativeMeta = declarative_base()


# Tag table
class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String)
    post_id = Column(Integer, ForeignKey("post.id"))
    __table_args__ = (UniqueConstraint("tag", "post_id", name="_tag_post_uc"),)


# Post table
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


# Gme table
class Gamestop(Base):
    __tablename__ = "gamestop"
    id = Column(Integer, primary_key=True, autoincrement=True)
    hour = Column(DateTime)
    openprice = Column(Float)
    lowprice = Column(Float)
    highprice = Column(Float)
    volume = Column(Integer)
    closeprice = Column(Float)  # target variable
    prediction = Column(Float)  # models predictions of closeprice


# Wide table
class Wide(Base):
    __tablename__ = "wide"
    id = Column(String, primary_key=True)

    hour = Column(DateTime)

    # Reddit columns (derived via aggregations)
    avg_all_post_pos = Column(Float)
    avg_all_post_neg = Column(Float)
    avg_all_post_neu = Column(Float)
    cnt_all_user = Column(Integer)
    cnt_all_tag = Column(Integer)
    cnt_all_post = Column(Integer)
    cnt_all_comments = Column(Integer)

    avg_gme_post_pos = Column(Float)
    avg_gme_post_neg = Column(Float)
    avg_gme_post_neu = Column(Float)
    cnt_gme_user = Column(Integer)
    cnt_gme_tag = Column(Integer)
    cnt_gme_post = Column(Integer)
    cnt_gme_comments = Column(Integer)

    # Financial columns (directly from gme table)
    openprice = Column(Float)
    lowprice = Column(Float)
    highprice = Column(Float)
    volume = Column(Integer)
    closeprice = Column(Float)  # target variable
    prediction = Column(Float)  # models predictions of closeprice
