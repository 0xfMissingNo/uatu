import os
from collections import OrderedDict
from getpass import getpass


class Environment:

    def __init__(self):
        self._components = OrderedDict()
        self.secrets = Secrets()

    @property
    def components(self):
        return self._components

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


class Component:
    setup_executed = False

    def __init__(self):
        self.construct_attr()

    @property
    def dependencies(self):
        return []

    def construct_attr(self):
        for dependency in self.dependencies:
            if dependency.__name__ not in self.component_names:
                ENV.components[dependency.__name__] = dependency()
            setattr(self, '_' + dependency.__name__, ENV.components[dependency.__name__])

    def setup(self):
        """Implemented by inherited class"""

    def cleanup(self):
        """Implemented by inherited class"""

    def run(self):
        """Implemented by inherited class"""

    @property
    def component_names(self):
        return [i.__class__.__name__ for i in ENV.components]

    def logger(self, msg):
        ENV.logger(f'{" " * 30}{self.__class__.__name__} | {msg}')

    @property
    def secrets(self):
        return ENV.secrets
