import logging
import os

from notetool.secret import read_secret
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

uri = read_secret(cate1='notecoin', cate2='dataset', cate3='db_path')
uri = uri or f'sqlite:///{os.path.abspath(os.path.dirname(__file__))}/data/notecoin.db'
# engine = create_engine(uri, echo=True)
meta = MetaData()
engine = create_engine(uri)
Base = declarative_base()

logging.info(f'uri:{uri}')


def create_session():
    # return scoped_session(sessionmaker(autocommit=True,autoflush=True,bind=engine))
    # return sessionmaker(autocommit=True, autoflush=True, bind=engine)()
    return sessionmaker(bind=engine)()


def create_all():
    Base.metadata.create_all(engine)
    session.commit()


class BaseTable(object):
    def __init__(self, *args, **kwargs):
        self.session = create_session()

    def json(self):
        res = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        return res


session = create_session()
