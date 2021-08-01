import time
import asyncio
import cbpro
from threading import Thread
from src import Universe


class PriceTracker(cbpro.WebsocketClient, Universe):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Universe.__init__(self)
        self.price = None

    def on_message(self, msg):
        if not msg.get('price'):
            return
        self.price = float(msg['price'])
        self.logger(self.price)

    def async_setup(self):
        return [self.async_start, self.keepalive]

    async def async_start(self):
        self.stop = False
        self.on_open()
        self._connect()
        await self._listen()
        self._disconnect()

    async def keepalive(self, interval=30):
        while self.ws.connected:
            self.ws.ping("keepalive")
            await asyncio.sleep(interval)

    async def _listen(self):
        super()._listen()
        await asyncio.sleep(10)

    def start(self):
        loops = (cb() for cb in [self.async_start, self.keepalive])
        self.thread = Thread(target=self.async_run, args=loops, daemon=True)
        self.thread.start()


class CoinBase(Universe):

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
    
    def async_setup(self):
        return self.wsClient.async_setup()

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
