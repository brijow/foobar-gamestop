from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import backref, relationship

Base: DeclarativeMeta = declarative_base()


# Many-to-many table connecting tag ids and comment ids
tag_2_comment = Table(
    "tag_2_comment",
    Base.metadata,
    Column("tag_id", Integer, ForeignKey("tag.tag_id")),
    Column("comment_id", Integer, ForeignKey("comment.comment_id")),
)

# Many-to-many table connecting tag ids and submission ids
tag_2_submission = Table(
    "tag_2_submission",
    Base.metadata,
    Column("tag_id", Integer, ForeignKey("tag.tag_id")),
    Column("submission_id", Integer, ForeignKey("submission.submission_id")),
)


# Tag table
class Tag(Base):
    __tablename__ = "tag"
    tag_id = Column(Integer, primary_key=True)
    noun = Column(String)

    submissions = relationship(
        "Submission", secondary=tag_2_submission, back_populates="tags"
    )
    comments = relationship("Comment", secondary=tag_2_comment, back_populates="tags")


# Comment table
class Comment(Base):
    __tablename__ = "comment"
    comment_id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey("submission.submission_id"))
    posted_on = Column(DateTime)
    parent_id = Column(Integer, ForeignKey("comment.comment_id"), index=True)

    sub_comments = relationship(
        "Comment", backref=backref("parent", remote_side=[comment_id])
    )
    tags = relationship("Tag", secondary=tag_2_comment, back_populates="comments")


# Submission table
class Submission(Base):
    __tablename__ = "submission"
    submission_id = Column(Integer, primary_key=True)
    subreddit = Column(String)
    user = Column(String)
    posted_on = Column(DateTime)

    comments = relationship("Comment", backref=backref("submission"))
    tags = relationship("Tag", secondary=tag_2_submission, back_populates="submissions")
