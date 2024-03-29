# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from instance.config import SQLALCHEMY_DATABASE_URI

# connect to the respective database
engine = create_engine(SQLALCHEMY_DATABASE_URI, convert_unicode=True)
# variable that allows for commits and rollbacks to database
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    """
    Method creates and initializes the models used
    :return: None
    """
    import app.models
    print(app.models)
    Base.metadata.create_all(bind=engine)
