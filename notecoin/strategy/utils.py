from notecoin.okex.client import AccountClient, AssetClient, MarketClient, PublicClient, TradeClient
from notetool.secret import read_secret

api_key = read_secret(cate1='coin', cate2='okex', cate3='api_key')
secret_key = read_secret(cate1='coin', cate2='okex', cate3='secret_key')
passphrase = read_secret(cate1='coin', cate2='okex', cate3='passphrase')

account_api = AccountClient(api_key, secret_key, passphrase)
funding_api = AssetClient(api_key, secret_key, passphrase)
market_api = MarketClient(api_key, secret_key, passphrase)
public_api = PublicClient(api_key, secret_key, passphrase)
trade_api = TradeClient(api_key, secret_key, passphrase)

