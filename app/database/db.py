import os
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# All models are going to need to inherit this singleton so they can join against each other
Base = declarative_base()

try:
    DATABASE_URL = os.environ["DATABASE_URL"]
except KeyError:
    DATABASE_URL = ""


def bind_engine(engine):
    Base.metadata.bind = engine
    Session.configure(bind=engine)


def rw_session():
    from sqlalchemy import create_engine

    engine = create_engine(DATABASE_URL)

    session = sessionmaker(engine)

    return session()


def get_db() -> Session:
    """Gets an instance of a DB session

    Because all of our models are interconnected we need to get the DB connection from one place
    so that SqlAlchemys base models know where and how to join

    :return: DB Session
    """
    session = rw_session()
    return session
