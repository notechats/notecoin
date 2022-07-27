from notecoin.strategy.utils import trade_api


class OkexCoin:
    def __init__(self, coin_id='METIS-USDT', price=0, count=0.):
        self.coin_id = coin_id
        self.count = count
        self.price_in = price
        self.price = self.price_in

    @property
    def money(self):
        return self.price * self.count

    def buy(self):
        return trade_api.place_order(instId=self.coin_id, tdMode='cash', side='buy', ordType='market', sz='50')

    def sell(self):
        return trade_api.place_order(instId=self.coin_id, tdMode='cash', side='sell', ordType='market', sz=self.count)

    @staticmethod
    def instance_by_account(data):
        okex = OkexCoin(coin_id=f"{data['ccy']}-USDT", count=float(data['availBal']),
                        price=float(data['eqUsd']) / float(data['availBal']))
        return okex

    @staticmethod
    def instance_by_new(coin_id):
        okex = OkexCoin(coin_id=coin_id)
        okex.buy()
        return okex

    def watch(self):
        if self.money > 51.2:
            self.sell()

    def __str__(self):
        return f"{self.coin_id}\t{self.count}\t{self.price_in}\t{self.price}\t{self.money}"

    def to_json(self):
        return {
            "coin_id": self.coin_id,
            "usdt": round(self.count * self.price, 2)
        }
