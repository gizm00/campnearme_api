#from flask.ext.sqlalchemy import SQLAlchemy
#db = SQLAlchemy()

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import *

conn_str = "postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}".format(
    DB_USER=DEV_DB_USER,
    DB_PASS=DEV_DB_PASS,
    DB_HOST=DEV_DB_HOST,
    DB_NAME=DEV_DB_NAME
)

engine = create_engine(conn_str, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)
