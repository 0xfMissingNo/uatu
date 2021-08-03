import os
import asyncio
from collections import OrderedDict
from getpass import getpass
from threading import Thread

class Environment:

    def __init__(self):
        self._universes = OrderedDict()
        self.secrets = Secrets()

    @property
    def universes(self):
        return self._universes

    @staticmethod
    def logger(msg):
        print(msg)


class Secrets:

    def get_password(self, param_name):
        password = self._get_password(param_name)
        if not password:
            self.set_password(param_name, getpass(f"Enter {param_name}: "))
            password = self._get_password(param_name)
        return password

    @staticmethod
    def _get_password(param_name):
        return os.getenv(param_name)

    @staticmethod
    def set_password(param_name, param_value):
        os.environ[param_name] = param_value

    @property
    def etherscan_token(self):
        return self.get_password("ETHERSCAN_TOKEN")

    @property
    def infura_project_id(self):
        return self.get_password("WEB3_INFURA_PROJECT_ID")

    @property
    def td_ameritrade_apikey(self):
        return self.get_password("TD_AMERITRADE_APIKEY")

    @property
    def td_ameritrade_account_number(self):
        return self.get_password("TD_AMERITRADE_ACCOUNT_NUMBER")

    @property
    def reddit_client_id(self):
        return self.get_password('REDDIT_CLIENT_ID')

    @property
    def reddit_client_secret(self):
        return self.get_password('REDDIT_CLIENT_SECRET')

    @property
    def reddit_client_username(self):
        return self.get_password('REDDIT_CLIENT_USERNAME')

    @property
    def twitter_consumer_key(self):
        return self.get_password("TWITTER_CONSUMER_KEY")

    @property
    def twitter_consumer_secret(self):
        return self.get_password("TWITTER_CONSUMER_SECRET")

    @property
    def twitter_access_token(self):
        return self.get_password("TWITTER_ACCESS_TOKEN")

    @property
    def twitter_access_token_secret(self):
        return self.get_password("TWITTER_ACCESS_TOKEN_SECRET")


ENV = Environment()
