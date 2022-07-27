import csv
import logging
import os
import warnings

import pandas as pd
from notesecret.secret import read_secret
from sqlalchemy import MetaData, Table, create_engine, delete, inspect, select
from sqlalchemy.orm import declarative_base
from tqdm import tqdm

uri = read_secret(cate1='notecoin', cate2='dataset', cate3='db_path')
uri = uri or f'sqlite:///{os.path.abspath(os.path.dirname(__file__))}/data/notecoin.db'


engine = create_engine(uri)
meta = MetaData(bind=engine)

Base = declarative_base()
logging.info(f'uri:{uri}')


def create_engines(url, **kwargs):
    return create_engine(url, **kwargs)


class BaseTable:
    def __init__(self, table_name, engine=engine, *args, **kwargs):
        self.table_name = table_name
        self.table: Table = None
        self.engine = engine

    def create(self):
        meta.create_all(self.engine)

    def insert(self, values, keys=None, *args, **kwargs):
        cols = [col.name for col in self.table.columns]
        if isinstance(values, dict):
            values = dict([(k, v) for k, v in values.items() if k in cols])
        elif isinstance(values, list):
            if isinstance(values[0], dict):
                values = [dict([(k, v) for k, v in item.items() if k in cols]) for item in values]
            elif isinstance(values[0], list):
                values = [dict(zip(keys, item)) for item in values]

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # code here...
            if str(self.engine.url).startswith('sqlite'):
                ins = self.table.insert(values=values).prefix_with("OR IGNORE")
            else:
                ins = self.table.insert(values=values).prefix_with("IGNORE")
            self.engine.execute(ins)

    def select_all(self):
        return self.engine.execute(select([self.table]))

    def delete_all(self):
        return self.engine.execute(delete(self.table))

    def to_csv(self, file_path, result=None):
        if result is None:
            result = self.select_all()
        with open(file_path, 'wb') as fw:
            out_csv = csv.writer(fw)
            out_csv.writerow(result.keys())
            out_csv.writerows(result)

    def to_csv_all(self, file_path, page_size=100000, total_step=1000):
        for step in tqdm(range(total_step)):
            start, stop = page_size * step, page_size * (step + 1)
            df = pd.read_sql(select([self.table]).slice(start, stop), self.engine)
            if len(df) == 0:
                break
            if start == 0:
                df.to_csv(file_path, header=True, index=False, mode='w')
            else:
                df.to_csv(file_path, header=False, index=False, mode='a')

    def upsert(self, values):
        if str(self.engine.url).startswith('mysql'):
            from sqlalchemy.dialects.mysql import insert
        elif str(self.engine.url).startswith('sqlite'):
            from sqlalchemy.dialects.sqlite import insert
        else:
            from sqlalchemy.dialects.postgresql import insert

        stmt = insert(self.table).values(values)
        primary_keys = [key.name for key in inspect(self.table).primary_key]
        update_dict = {c.name: c for c in stmt.excluded if
                       not c.primary_key and c.name not in ('gmt_create', 'gmt_creat')}
        stmt = stmt.on_conflict_do_update(index_elements=primary_keys, set_=update_dict)
        self.engine.execute(stmt)
