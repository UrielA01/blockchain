import requests
from typing import List

from src.core.blocks.block import Block
from src.core.transactions.transaction import Transaction
from src.utils.io_known_nodes import remove_known_node
from src.wallet.wallet import Wallet

class NodeException(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)
        self.message = message

    def __str__(self):
        return self.message

class Node:
    def __init__(self, ip= "127.0.0.1", port = 5000):
        self.ip = ip
        self.port = port
        self.hostname = f'http://{ip}:{port}'

    def post(self, path: str, data: dict) -> requests.Response:
        try:
            url = f"{self.hostname}{path}"
            req_return = requests.post(url, json=data)
            req_return.raise_for_status()
            if req_return.status_code == 200:
                return req_return.json()
            else:
                raise NodeException(f"Unexpected status code {req_return.status_code} from {url}")
        except requests.ConnectionError:
            print(f'Unable to connect to node - {self.hostname}')
            print(f'Removing node - {self.hostname} - from network_nodes.js')
            remove_known_node(self.to_dict)

    def get(self, path: str):
        try:
            url = f"{self.hostname}{path}"
            req_return = requests.get(url)
            req_return.raise_for_status()
            if req_return.status_code == 200:
                return req_return.json()
            else:
                raise NodeException(f"Unexpected status code {req_return.status_code} from {url}")
        except requests.ConnectionError:
            print(f'Unable to connect to node - {self.hostname}')
            print(f'Removing node - {self.hostname} - from network_nodes.js')
            remove_known_node(self.to_dict)

    @property
    def to_dict(self):
        return {
            "base_url": self.hostname,
            "ip": self.ip,
            "port": self.port
        }

    @staticmethod
    def from_json(node: dict) -> 'Node':
        return Node(node['ip'], node['port'])

    def get_known_nodes(self) -> List[dict]:
        return self.get("/known_nodes")

    def advertise(self, node: dict) -> requests.Response:
        return self.post("/advertise", {"node": node})

    def get_blockchain(self):
        return self.get("/chain")

    def ping(self):
        return self.get("/")

    def __eq__(self, other):
        return self.ip == other.ip and self.port == other.port

from src.network.network import Network
class SendNode:
    def __init__(self, network: Network, wallet: Wallet = Wallet()):
        self.wallet = wallet
        self.network = network

    def broadcast_post(self, path: str, data: dict):
        for node in self.network.known_nodes:
            node.post(path, data)

    def broadcast_get(self, path: str):
        for node in self.network.known_nodes:
            node.get(path)

    def broadcast_transaction(self, transaction: Transaction, path: str="/transaction"):
        transaction.sign_inputs(owner=self.wallet)
        self.broadcast_post(path, {"transaction": transaction.send_to_nodes()})

    def broadcast_block(self, block: Block, path: str="/block"):
        self.broadcast_post(path, {"block": block.to_dict})

