import time

import cbpro

from src import Component


class PriceTracker(cbpro.WebsocketClient, Component):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price = None

    def on_message(self, msg):
        if not msg.get('price'):
            return
        self.price = float(msg['price'])
        self.logger(self.price)


class CoinBase(Component):

    products = NotImplemented
    uri = "wss://ws-feed.pro.coinbase.com"
    _client = PriceTracker

    def __init__(self):
        super().__init__()
        self._started = False
        self.wsClient = self._client(  # pylint:disable=invalid-name
            url=self.uri,
            products=self.products,
            channels=["ticker"]
        )

    @property
    def is_running(self):
        return self._started

    def setup(self):
        if not self.is_running:
            self.start()

    def cleanup(self):
        self.close()

    def start(self):
        self._started = True
        self.wsClient.start()

    def close(self):
        self.wsClient.close()
        self._started = False

    @property
    def price(self):
        if not self.is_running:
            self.start()
        price = self.wsClient.price
        while price is None:
            time.sleep(1)
            price = self.wsClient.price
        return price


class CoinBaseProETH(CoinBase):

    class ETHPriceCBPro(PriceTracker):
        """wrapped"""
    _client = ETHPriceCBPro
    products = "ETH-USD"
