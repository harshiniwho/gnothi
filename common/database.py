import os
from box import Box
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from common.utils import vars, utcnow
# just for fastapi-users (I'm using sqlalchemy+engine+session everywhere else)
import databases
import logging
from contextlib import contextmanager
logger = logging.getLogger(__name__)

Base = declarative_base()

engine = create_engine(
    vars.DB_FULL,
    # TODO getting timout errors, trying some solutions
    # https://stackoverflow.com/a/60614871/362790
    # https://docs.sqlalchemy.org/en/13/core/pooling.html#dealing-with-disconnects
    # https://medium.com/@heyjcmc/controlling-the-flask-sqlalchemy-engine-a0f8fae15b47
    pool_pre_ping=True,
    pool_recycle=300,
)
engine_books = create_engine(
    vars.DB_BOOKS,
    pool_pre_ping=True,
    pool_recycle=300,
)
print(engine)

Sessions = dict(
    main=sessionmaker(autocommit=False, autoflush=False, bind=engine),
    books=sessionmaker(bind=engine_books)  # never saving to this db anyway
)

@contextmanager
def session(k='main', commit=True):
    sess = Sessions[k]()
    try:
        yield sess
        if commit:
            sess.commit()
    except:
        sess.rollback()
        raise
    finally:
        sess.close()


fa_users_db = databases.Database(vars.DB_FULL)


def init_db():
    engine.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    # add `import app.models` in calling code beforehand (after `import database`)
    Base.metadata.create_all(bind=engine)
    # e6dfbbd8: kick off create_all with sess.execute()
    engine.execute("select 1")


def shutdown_db():
    # using context-vars session-makers now
    pass
