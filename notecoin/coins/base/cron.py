import logging
import os

from ccxt import okex
from notecoin.coins.base.file import DataFileProperty

logger = logging.getLogger()
logger.setLevel(logging.INFO)

path_root = '/home/bingtao/workspace/tmp'

file_pro = DataFileProperty(exchange=okex(), freq='daily', path=path_root, timeframe='1m')
file_pro.load(total=365)
file_pro .change_freq('weekly')
file_pro.load(total=54)
file_pro .change_freq('monthly')
file_pro.load(total=12)
# nohup /home/bingtao/opt/anaconda3/bin/python /home/bingtao/workspace/notechats/notecoin/notecoin/coins/base/cron.py >>/notechats/notecoin/logs/notecoin-$(date +%Y-%m-%d).log 2>&1 &
