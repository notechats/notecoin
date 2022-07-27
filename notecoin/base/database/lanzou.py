from notecoin.base.database.base import BaseTable, engine, meta
from notedrive.lanzou import LanZouDrive
from sqlalchemy import BIGINT, TIMESTAMP, Column, String, Table, func, select


class LanzouDirectory(BaseTable):
    def __init__(self, table_name="notecoin_lanzou", fid=5679873, *args, **kwargs):
        self.fid = fid
        super(LanzouDirectory, self).__init__(table_name=table_name, engine=engine, *args, **kwargs)
        self.table = Table(self.table_name, meta,
                           Column('fid', BIGINT, comment='fid', primary_key=True),
                           Column('gmt_create', TIMESTAMP(True), server_default=func.now()),
                           Column('gmt_modified', TIMESTAMP(True), server_default=func.now()),
                           Column('isfile', BIGINT, comment='是否文件', default='1'),
                           Column('name', String(100), comment='名称', default=''),
                           Column('path', String(500), comment='路径', default=''),
                           )
        self.create()
        self.drive = LanZouDrive()
        self.drive.ignore_limits()
        self.drive.login_by_cookie()

    def scan_all_file(self, clear=False):
        if clear:
            self.delete_all()
        self._scan_all_file(self.fid, 'notecoin')

    def _scan_all_file(self, fid, path):
        for _dir in self.drive.get_dir_list(fid):
            data = {
                "fid": _dir.id,
                "name": _dir.name,
                "path": f'{path}/{_dir.name}',
                "isfile": 0
            }
            self.insert(values=data)
            self._scan_all_file(fid=data['fid'], path=data['path'])

        for _file in self.drive.get_file_list(fid):
            data = {
                "fid": _file.id,
                "name": _file.name,
                "path": f'{path}/{_file.name}',
                "isfile": 1
            }
            self.insert(values=data)

    def file_exist(self, path):
        s = select(self.table.columns).where(self.table.columns.path == path)
        data = [line for line in engine.execute(s)]
        return len(data) == 1

    def file_fid(self, path):
        s = select(self.table.columns).where(self.table.columns.path == path)
        data = [line for line in engine.execute(s)]

        if len(data) == 1:
            return data[0]['fid']
        else:
            return -1

    def sync(self, path):
        def filter_fun(x): return x.endswith('.csv')
        self.drive.sync_files(path, self.fid, remove_local=True, filter_fun=filter_fun)
