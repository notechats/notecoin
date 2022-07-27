from .model import KlineDetail

okex_kline_1min = KlineDetail(db_path='/home/bingtao/workspace/tmp/coin.db', table_name='okex_kline_1min')
okex_kline_5min = KlineDetail(db_path='/home/bingtao/workspace/tmp/coin.db', table_name='okex_kline_5min')
okex_kline_1min.create()
okex_kline_5min.create()