from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Float,
    Boolean,
)
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import backref, relationship

Base: DeclarativeMeta = declarative_base()


# Tag table
class Tag(Base):
    __tablename__ = "tag"
    token = Column(String, primary_key=True)
    post_id = Column(Integer, ForeignKey("post.id"))


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
