
import time
from threading import Thread

from src import ENV
from src.coinbase import CoinBaseProETH
from src.infura import EthereumMemPool
from src.twitter import ETHTwitterBot


class TheWatcher:

    _components = ()

    def __init__(self):
        self._is_running = False
        self.thread = None

    @property
    def components(self):
        return ENV.components

    def logger(self, msg):
        ENV.logger(f'{self.__class__.__name__} | {msg}')

    def initialize(self):
        self.logger('initializing')
        for component in self._components:
            if component in [i.__class__ for i in ENV.components]:
                continue
            init = component()
            self.components[init.__class__.__name__] = init

    def setup(self):
        for component in self.components:
            self.components[component].setup()
            self.components[component].setup_executed = True

    def component_run(self):
        for component in self.components:
            self.components[component].run()

    def cleanup(self):
        for component in list(self.components)[::-1]:
            try:
                if not self.components[component].setup_executed:
                    continue
                self.components[component].cleanup()
            except Exception:
                pass

    def _run(self):
        self.initialize()
        try:
            self.setup()
            self.component_run()
            self.execute()
        finally:
            self.cleanup()

    def execute(self):
        self._is_running = True
        while self._is_running:
            time.sleep(1)

    def run(self):
        self.thread = Thread(target=self._run, args=(), daemon=True)
        self.thread.start()

    def close(self):
        self._is_running = False
        self.thread.join()


class Uatu(TheWatcher):

    _components = ETHTwitterBot, CoinBaseProETH, EthereumMemPool
