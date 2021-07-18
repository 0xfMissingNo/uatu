import json
from collections import defaultdict
from threading import Thread

import websocket
from etherscan import Client
from web3 import Web3
from websocket import create_connection
from websocket._exceptions import WebSocketConnectionClosedException

from src import Component
from src.coinbase import CoinBaseProETH


class InfuraWSS(Component):

    __ref__ = 'https://infura.io/docs/ethereum/wss/introduction'
    uri = "wss://mainnet.infura.io/ws/v3/"
    jsonrpc = "2.0"
    _env_name = 'WEB3_INFURA_PROJECT_ID'

    def _create_attr(self, hidden_attr, callback):
        if hasattr(self, hidden_attr):
            return getattr(self, hidden_attr)
        project_id = self.secrets.infura_project_id
        setattr(self, hidden_attr, callback(self.uri + project_id))
        return getattr(self, hidden_attr)

    @property
    def web3(self):
        def make_w3(url):
            # TODO: why no-member?
            return Web3(Web3.WebsocketProvider(url))  # pylint:disable=no-member
        return self._create_attr('__web3', make_w3)

    @property
    def conn(self):
        return self._create_attr('__conn', create_connection)

    def send(self, msg):
        return self.conn.send(json.dumps(msg))

    def recv(self):
        try:
            return json.loads(self.conn.recv())
        except (
            json.decoder.JSONDecodeError,
            WebSocketConnectionClosedException,
            websocket._socket.ssl.SSLError  # pylint:disable=protected-access
        ):
            return {}

    @staticmethod
    def _get_hash_from_id(id_, method):
        items = id_[len(method) + 1:][2:-2]
        if ',' not in items:
            return items
        return items.split(',')[0][:-1]

    def _send_method(self, method, param=None):
        if not param:
            param = []
        if not isinstance(param, list):
            param = [param]
        return self.send(
            {
                "jsonrpc": self.jsonrpc,
                "id": method + '_' + str(param),
                "method": method,
                "params": param
            }
        )


class InfuraSubscription(InfuraWSS):

    def __init__(self):
        super().__init__()
        self._subscribed = defaultdict(bool)
        self._max_eth_value = 0
        self._hash = None
        self.thread = None

    @property
    def dependencies(self):
        return [CoinBaseProETH]

    @property
    def eth(self):
        return getattr(self, '_CoinBaseProETH')

    def callback(self):
        data = self.get_tx_by_hash()
        if not data:
            return

        if not data['id'].startswith('eth_getTransactionByHash'):
            return

        self.inner_callback(data)

    def inner_callback(self, data):
        raise NotImplementedError()

    def eth_to_usd(self, eth_value, as_str=False):
        usd_value = (int(eth_value, 16) / 10 ** 18) * self.eth.price
        if as_str:
            return "{:.2f}".format(usd_value)
        return usd_value

    def get_tx_by_hash(self):
        data = self.recv()
        if data.get('method', '').startswith('eth_subscription'):
            hash_ = data['params']['result']
            self._send_method('eth_getTransactionByHash', hash_)
            return None
        if not data.get('result'):
            return None
        return data

    def is_subscribed(self, param):
        return self._subscribed[param]

    def subscribe(self, param):
        if self.is_subscribed(param):
            return
        self._send_method("eth_subscribe", param)
        self._subscribed[param] = True

        def subscription():
            while self.is_subscribed(param):
                self.callback()
        self.thread = Thread(target=subscription, daemon=True)
        self.thread.start()

    def unsubscribe(self, param):
        if not self.is_subscribed(param):
            return
        self._send_method("eth_unsubscribe", param)
        self._subscribed[param] = False

    def close(self):
        subscriptions = self._subscribed.keys()
        for subscription in subscriptions:
            self._subscribed[subscription] = False
        self.conn.close()
        delattr(self, '__conn')
        self.thread.join()

    def setup(self):
        return self.subscribe('newPendingTransactions')

    def cleanup(self):
        return self.close()


class SourceCodeAnalysis(InfuraSubscription):

    def __init__(self):
        super().__init__()
        self.etherscan = Client(self.secrets.etherscan_token)
        self.contract_addresses = set()

    def inner_callback(self, data):

        if data['id'].startswith('eth_getTransactionByHash'):
            self._send_method(data['result']['to'])
            self._send_method(data['result']['from'])

        if not data['id'].startswith('eth_getCode'):
            return None

        address = self._get_hash_from_id(data['id'], 'eth_getCode')
        self.contract_addresses.add(address)

        if {address} - self.contract_addresses:
            self.contract_addresses.add(address)
            # TODO: why no-memeber
            source = self.etherscan.get_contract_source_code(address)  # pylint:disable=no-member
            self.logger(source)

        return source


class PrintIncrementingTX(InfuraSubscription):

    def inner_callback(self, data):

        eth_value = self.eth_to_usd(data['result']['value'])
        tx_hash = data['result']['hash']

        if self._max_eth_value < eth_value:
            self.logger(f'{tx_hash} - ${"{:.2f}".format(eth_value)}')
            self._hash = tx_hash
            self._max_eth_value = eth_value


class EthereumMemPool(InfuraSubscription):

    def inner_callback(self, data):

        eth_value = self.eth_to_usd(data['result']['value'])
        if not float(eth_value):
            return
        tx_hash = data['result']['hash']
        self.logger(f'{tx_hash} - ${"{:.2f}".format(eth_value)}')
