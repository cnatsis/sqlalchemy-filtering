from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import functions

Base = declarative_base()


def compile_query_postgres(query):
    from sqlalchemy.dialects import postgresql
    return str(query.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


def compile_query_sqlite(query):
    from sqlalchemy.dialects import sqlite
    return str(query.statement.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True}))


class UserInfo(Base):
    __tablename__ = "user_info"

    id = Column(Integer, primary_key=True, index=True)
    details = Column(JSONB)
    creation_date = Column(DateTime, nullable=False, server_default=functions.now())


class Ratings(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    creation_date = Column(DateTime, nullable=False, server_default=functions.now())
    movie_name = Column(String)
    rating = Column(Float)
