import asyncio
from threading import Thread
from src import ENV


def runner(func):
    async def inner(self, *args, **kwargs):
        while self.connected:
            if self.running:
                func(self, *args, **kwargs)
                await asyncio.sleep(self.delay)
    return inner

class AsyncManager:
    delay = 1 / 10 ** 6

    @property
    def async_methods(self):
        return []
    
    @property
    def loops(self):
        return (cb() for cb in self.async_methods)
    
    def 

class Universe:
    setup_executed = False

    def async_setup(self):
        return []

    async def gather(self, *args):
        await asyncio.gather(*args)
    
    def async_run(self):
        loops = (cb() for cb in self.async_setup())
        return asyncio.run(self.gather(*loops))

    def start_thread(self):
        self.thread = Thread(target=self.async_run)
        self.thread.start()

    def __init__(self):
        self.construct_attr()

    @property
    def dependencies(self):
        return []

    def construct_attr(self):
        for dependency in self.dependencies:
            if dependency.__name__ not in self.universe_names:
                ENV.universes[dependency.__name__] = dependency()
            setattr(self, '_' + dependency.__name__, ENV.universes[dependency.__name__])

    def setup(self):
        """Implemented by inherited class"""

    def cleanup(self):
        """Implemented by inherited class"""

    def run(self):
        """Implemented by inherited class"""

    @property
    def universe_names(self):
        return [i.__class__.__name__ for i in ENV.universes]

    def logger(self, msg):
        return ENV.logger(f'{" " * 30}{self.__class__.__name__} | {msg}')

    @property
    def secrets(self):
        return ENV.secrets
