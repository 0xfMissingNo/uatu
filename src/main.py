
import time
from threading import Thread
import asyncio
from src.base import CrossClassAsyncManager
from src import ENV
from src.coinbase import CoinBaseProETH
from src.infura import EthereumMemPool
from src.twitter import ETHTwitterBot


class Multiverse(CrossClassAsyncManager):

    _universes = ()

    def __init__(self):
        self._is_running = False
        self.thread = None

    @property
    def universes(self):
        return ENV.universes

    def logger(self, msg):
        ENV.logger(f'{self.__class__.__name__} | {msg}')

    def initialize(self):
        self.logger('initializing')
        for universe in self._universes:
            if universe in [i.__class__ for i in ENV.universes]:
                continue
            init = universe()
            self.universes[init.__class__.__name__] = init

    def setup(self):
        for universe in self.universes:
            self.universes[universe].setup()
            self.universes[universe].setup_executed = True

    def universe_run(self):
        for universe in self.universes:
            self.universes[universe].run()

    def cleanup(self):
        for universe in list(self.universes)[::-1]:
            try:
                if not self.universes[universe].setup_executed:
                    continue
                self.universes[universe].cleanup()
            except Exception:
                pass

    def _run(self):
        self.initialize()
        try:
            self.setup()
            self.universe_run()
            self.execute()
        finally:
            self.cleanup()

    def execute(self):
        self._is_running = True
        while self._is_running:
            time.sleep(.01)

    def run(self):
        self.thread = Thread(target=self._run, args=(), daemon=True)
        self.thread.start()

    def close(self):
        self._is_running = False
        self.thread.join()


class Uatu(Multiverse):
    _universes = ETHTwitterBot, CoinBaseProETH
