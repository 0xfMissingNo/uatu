import asyncio
from threading import Thread
from src import ENV


def event_loop(func):
    async def inner(self, *args, **kwargs):
        while self.connected:
            if self.running:
                func(self, *args, **kwargs)
                await asyncio.sleep(self.delay)
    return inner


class AsyncManager:

    delay = 1 / 10 ** 6

    def __init__(self):
        self.connected = False
        self.running = False
        self.thread = None

    @property
    def async_methods(self):
        return []
    
    @property
    def loops(self):
        return (cb() for cb in self.async_methods)

    def logger(self, msg):
        return ENV.logger(f'{" " * 30}{self.__class__.__name__} | {msg}')

    @asyncio.coroutine
    def asyncio_gather(self, *args):
        asyncio.gather(*args)
    
    def asyncio_run(self, *args):
        self.resume()
        return asyncio.run(self.asyncio_gather(*args))

    def start(self):
        self.thread = Thread(target=self.asyncio_run, daemon=True, args=self.loops)
        self.thread.start()

    def stop(self):
        self.pause()
        if self.thread and self.thread.is_alive():
            self.connected = False
            self.thread.join()
            self.thread = None
            return
        self.connected = False    

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True
        self.connected = True


class CrossClassAsyncManager(AsyncManager):

    _classes = ()

    def __init__(self):
        super().__init__()
        self.classes = (class_() for class_ in self._classes)

    @property
    def async_methods(self):
        methods = []
        for class_ in self.classes:
            methods += class_.async_methods
        return methods

    @property
    def loop(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        return (loop() for loop in [self._consolidate_loops])

    @asyncio.coroutine
    def _consolidate_loops(self):
        for loop in asyncio.as_completed(
            list(super(CrossClassAsyncManager, self).loops)
            ):
            yield from loop

    def start(self, *args):
        for class_ in self.classes:
            class_.resume()
        super().start(*args)
    
    def stop(self):
        for class_ in self.classes:
            class_.stop()
        super().stop()


class Universe(AsyncManager):

    setup_executed = False

    def __init__(self):
        super().__init__()
        self.construct_attr()

    def construct_attr(self):
        for dependency in self.dependencies:
            if dependency.__name__ not in self.universe_names:
                ENV.universes[dependency.__name__] = dependency()
            setattr(self, '_' + dependency.__name__, ENV.universes[dependency.__name__])

    @property
    def universe_names(self):
        return [i.__class__.__name__ for i in ENV.universes]

    @property
    def secrets(self):
        return ENV.secrets

    @property
    def dependencies(self):
        return []

    def setup(self):
        """Implemented by inherited class"""

    def cleanup(self):
        """Implemented by inherited class"""

    def run(self):
        """Implemented by inherited class"""
