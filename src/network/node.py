from typing import List

import requests

from src.core.blocks import Block
from src.core.transactions.transaction import Transaction
from src.wallet.wallet import Wallet


class Node:
    def __init__(self, ip= "127.0.0.1", port = 5000):
        self.base_url = f'http://{ip}:{port}'

    def post(self, path: str, data: dict) -> requests.Response:
        url = f"{self.base_url}{path}"
        req_return = requests.post(url, json=data)
        req_return.raise_for_status()
        return req_return

class SendNode:
    def __init__(self, wallet: Wallet = Wallet()):
        self.wallet = wallet
        self.nodes_in_network = [Node("127.0.0.1", 5001),
                                    Node("127.0.0.1", 5002)]

    def broadcast(self, path: str,  data: dict):
        for node in self.nodes_in_network:
            try:
                node.post(path, data)
            except requests.ConnectionError:
                print(f'Unable to connect to node - {node.base_url}')

    def broadcast_transaction(self, transaction: Transaction, path: str="/transaction"):
        transaction.sign_inputs(owner=self.wallet)
        self.broadcast(path, {"transaction": transaction.send_to_nodes()})

    def broadcast_block(self, block: Block, path: str="/blocks"):
        self.broadcast(path, {"blocks": block.to_dict})


class ReceiveNode:
    def __init__(self):
        self.transactions_data: List[Transaction] = []