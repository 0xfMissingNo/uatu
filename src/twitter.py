import re
import sys
from threading import Thread
import asyncio
import aiohttp
import tweepy
import ssl
from requests.exceptions import Timeout
from langdetect import detect, lang_detect_exception

from src import Universe


class BaseListener(tweepy.StreamListener, Universe):

    __ref__ = "http://docs.tweepy.org/en/latest/streaming_how_to.html"
    _regex = r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)"

    @staticmethod
    def is_english(text):
        try:
            if detect(text) == 'en':
                return True
        except lang_detect_exception.LangDetectException:
            pass
        return False

    def on_status(self, status):
        text = ' '.join(re.sub(self._regex, " ", status.text).split())
        if not self.is_english(text):
            return
        self.logger(text)

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_error disconnects the stream
            return False
        return True


class AsyncStream(tweepy.Stream, Universe):

    def async_setup(self):
        return [self._run]
    
    def _start(self, is_async):
        """Intentionally overridden"""

    @asyncio.coroutine
    def _run(self):
        super()._run()

    async def filter(self, *args, **kwargs):
        super().filter(*args, **kwargs)
        self.running = True
        await self._run()


class BaseTwitterBot(Universe):

    __ref__ = "http://docs.tweepy.org/en/latest/"
    twitter_handles = []
    symbol = None
    _listener = BaseListener
    _stream = AsyncStream

    def async_setup(self):
        return [self.track]

    def __init__(self):
        super().__init__()
        self.keywords = []
        self._stream_initialized = True
        self.auth = tweepy.OAuthHandler(
            self.secrets.twitter_consumer_key,
            self.secrets.twitter_consumer_secret
        )
        self.auth.set_access_token(
            self.secrets.twitter_access_token,
            self.secrets.twitter_access_token_secret
        )

        self.api = tweepy.API(self.auth)
        self._init_stream()

    def _init_stream(self):
        self.stream = self._stream(auth=self.auth, listener=self.listener())
        self._stream_initialized = True

    async def track(self, keywords=None, symbol='$ETH'):

        if not self._stream_initialized:
            self._init_stream()

        if not keywords:
            keywords = []

        if not isinstance(keywords, list):
            keywords = [keywords]

        if symbol:
            if not symbol.startswith('$'):
                raise ValueError('symbol should start with "$"')
            keywords += [symbol, symbol[1:]]
            self.symbol = symbol[1:]
        self.keywords = keywords
        self.logger(f'Initializing twitter bots for {keywords} with {self.__class__.__name__}')

        await self.stream.filter(track=keywords, is_async=True)

    async def follow(self, twitter_names=None):

        if not self._stream_initialized:
            self._init_stream()

        if not twitter_names:
            twitter_names = []
        if isinstance(twitter_names, str):
            twitter_names = [twitter_names]
        if self.twitter_handles:
            twitter_names += self.twitter_handles

        twitter_id_list = [str(self.api.get_user(name).id) for name in twitter_names]
        await self.stream.filter(follow=twitter_id_list, is_async=True)

    def disconnect(self):
        self._stream_initialized = False
        return self.stream.disconnect()

    def listener(self):
        """Not Implemented"""
        tweet = self._listener()
        return tweet

    def cleanup(self):
        self.disconnect()


class WhaleTrades(BaseTwitterBot):
    twitter_handles = ['WhaleTrades', 'WhaleCalls', 'Deribot']

    def run(self):
        self.follow()


class ETHTwitterBot(BaseTwitterBot):

    class ETHTwitter(BaseListener):
        """wrapped"""
    _listener = ETHTwitter

    def async_setup(self):
        return [self.track]
