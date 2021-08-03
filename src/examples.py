from src.base import event_loop, AsyncManager, CrossClassAsyncManager


class Example(AsyncManager):
    
    @property
    def async_methods(self):
        return [self.loopa, self.loopb, self.loopc]

    @event_loop
    def loopa(self):
        self.logger(' ' * 30 + f'{self}: loop a')

    @event_loop
    def loopb(self):
        self.logger(' ' * 30 + f'{self}: loop b')

    @event_loop
    def loopc(self):
        self.logger(' ' * 30 + f'{self}: loop c')


class Example1(Example):
    """changes class name"""


class Example2(Example):
    """changes class name"""


class Example3(Example):
    """changes class name"""


class ExampleCrossClassAsyncManager(CrossClassAsyncManager):
    _classes = Example1, Example2, Example3
