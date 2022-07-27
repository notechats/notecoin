import time
from typing import Dict

from notebuild.tool.fastapi import add_api_routes, api_route
from notecoin.database.base import create_all, create_session
from notecoin.database.connect import RedisConnect
from notecoin.okex.database.client import OkexClientAccountBalance
from notecoin.okex.database.strategy import OkexStrategyAutoSeller
from notecoin.okex.database.websocket import OkexSocketPublicTickers


class AutoSeller(RedisConnect):
    def __init__(self, prefix="/sell", *args, **kwargs):
        self.total = 0
        self.usdt = 0

        self.session = create_session()
        create_all()
        self.db_account: Dict[str, OkexClientAccountBalance] = {}
        self.db_seller: Dict[str, OkexStrategyAutoSeller] = {}

        super(AutoSeller, self).__init__(prefix=prefix, *args, **kwargs)
        add_api_routes(self)

    def load_account(self):
        self.db_account.clear()
        self.db_seller.clear()
        for detail in self.session.query(OkexClientAccountBalance).all():
            if detail.availBal > 1:
                self.db_account[detail.ccy] = detail
        for detail in self.session.query(OkexStrategyAutoSeller).all():
            self.db_seller[detail.coin_id] = detail
        return {}

    def update_price(self):
        details = self.session.query(OkexSocketPublicTickers).all()
        data_map = dict([(detail.instId, detail.last) for detail in details])

        for aa in self.db_account.values():
            coin_id = aa.ccy if aa.ccy == 'USDT' else f"{aa.ccy}-USDT"
            if coin_id not in self.db_seller.keys():
                tmp = OkexStrategyAutoSeller.instance(coin_id=coin_id,
                                                      worth=aa.eqUsd,
                                                      init_worth=50,
                                                      count=aa.availBal,
                                                      price=aa.eqUsd / aa.availBal)
                self.session.merge(tmp)
                self.session.commit()
            if coin_id not in self.db_seller.keys():
                continue
            price = data_map.get(coin_id, 1.0)
            coin_seller = self.db_seller[coin_id]
            coin_seller.update_worth(worth=price * aa.availBal, count=aa.availBal, price=price)
        return {
            # "price_size": len(data_map),
            # "price_data": data_map
        }

    def to_json(self):
        self.total = self.usdt
        for coin in self.db_seller.values():
            self.total += coin.worth

        return {
            "total": round(self.total, 2),
            "res": round(self.usdt, 2),
            "coins": [coin.to_json() for coin in self.db_seller.values()]
        }

    @api_route("/update")
    def update_value(self, suffix=""):
        res = {}
        res.update(self.load_account())
        res.update(self.update_price())

        for coin in self.db_seller.values():
            if coin.coin_id == 'USDT':
                self.usdt = coin.worth
                continue
            if coin.check():
                coin.sell()
                self.session.query(OkexStrategyAutoSeller).filter(
                    OkexStrategyAutoSeller.coin_id == coin.coin_id).delete()
            else:
                self.session.merge(coin)
            self.session.commit()
        update_time = int(round(time.time() * 1000)) - 60 * 60 * 1000
        self.session.query(OkexStrategyAutoSeller).filter(OkexStrategyAutoSeller.updateTime < update_time).delete()
        self.session.commit()
        res.update(self.to_json())
        return res
