import os.path
import sqlite3
from aifc import Error

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_filename = '../test/filter.db'

engine = create_engine(
    'sqlite:///{}'.format(db_filename)
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    if not os.path.isfile(db_filename):
        open(db_filename, "w+").close()

    conn = None
    try:
        conn = sqlite3.connect(db_filename)
        print(open('sql/postgresql_tables.sql').read().strip())
        conn.executescript(open('sql/postgresql_tables.sql').read().strip())
        conn.commit()
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def destroy_db():
    os.remove(db_filename)
