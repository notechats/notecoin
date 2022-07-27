from ccxt import okex
from fastapi import APIRouter
from notebuild.tool.fastapi import add_api_routes, api_route
from notecoin.coins.base.file import DataFileProperty

path_root = '/home/bingtao/workspace/tmp'


class DownloadServer(APIRouter):
    def __init__(self, prefix='/download', *args, **kwargs):
        super(DownloadServer, self).__init__(prefix=prefix, *args, **kwargs)
        add_api_routes(self)

    @api_route('/kline', description="get value")
    def download_kline(self, freq='daily', timeframe='1m'):
        file_pro = DataFileProperty(exchange=okex(), freq=freq, path=path_root, timeframe=timeframe)
        file_pro.load()
