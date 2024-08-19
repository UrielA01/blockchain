import time
from dataclasses import asdict, dataclass, field
from typing import List, Set
from urllib.parse import urlparse

import requests

from .block import Block
from .consensus import Consensus
from .transaction import Transaction


@dataclass
class Blockchain:
    last_block: Block = field(default_factory=lambda: Block(
        index=1,
        timestamp=time.time(),
        transactions=[],
        previous_hash=None,
        previous_block=None
    ))
    length: int = 1
    current_transactions: List[Transaction] = field(default_factory=list)
    nodes: Set[str] = field(default_factory=set)
    consensus: Consensus = field(default_factory=Consensus)

    def add_block(self) -> Block:
        block = Block(
            index=self.length + 1,
            timestamp=time.time(),
            transactions=self.current_transactions,
            previous_hash=self.last_block.previous_hash,
            previous_block=self.last_block,
        )

        self.length += 1

        nonce = self.consensus.proof_of_work(block)
        block.nonce = nonce
        block.hash = block.compute_hash()
        self.current_transactions = []

        self.broadcast_block(block)
        return block

    def receive_block(self, block: Block) -> bool:
        if self.consensus.valid_new_block(new_block=block, last_block=self.last_block):
            block.previous_block = self.last_block
            self.last_block = block
            return True

        return False

    def new_transaction(self, transaction: Transaction) -> int:
        timestamps = [
            transaction.timestamp for transaction in self.current_transactions]
        if transaction.timestamp in timestamps:
            raise Exception("Transaction already exists")
        self.current_transactions.append(transaction)
        return self.last_block.index + 1

    def register_node(self, address: str) -> None:
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """
        try:
            parsed_url = urlparse(address)
            self.nodes.add(parsed_url.netloc)
        except AttributeError:
            raise ValueError("Invalid URL")

    # Going to be deprecated
    # def resolve_conflicts(self) -> bool:
    #     """
    #     This is our Consensus Algorithm, it resolves conflicts
    #     by replacing our chain with the longest one in the network.
    #     :return: <bool> True if our chain was replaced, False if not
    #     """
    #     neighbours = self.nodes
    #     new_chain = None

    #     # We're only looking for chains longer than ours
    #     max_length = len(self.chain)

    #     # Grab and verify the chains from all the nodes in our network
    #     for node in neighbours:
    #         response = requests.get(f'http://{node}/chain')

    #         if response.status_code == 200:
    #             length = response.json()["length"]
    #             chain_data = response.json()["chain"]

    #             block = Block(**chain_data.last_block)

    #             # Check if the length is longer and the chain is valid
    #             if length > max_length and self.consensus.valid_chain(chain):
    #                 max_length = length
    #                 new_chain = chain

    #     # Replace our chain if we discovered a new, valid chain longer than ours
    #     if new_chain:
    #         self.chain = new_chain
    #         return True

    #     return False

    # def get_balance(self, address: bytes) -> int:
    #     balance = 0
    #     for block in self.chain:
    #         for transaction in block.transactions:
    #             if transaction.sender == address:
    #                 balance -= transaction.amount
    #             if transaction.recipient == address:
    #                 balance += transaction.amount
    #     return balance

    def broadcast_transaction(self, transaction: Transaction):
        for node in self.nodes:
            response = requests.post(
                f'http://{node}/transactions/receive', json=asdict(transaction))
            if response.status_code != 201:
                raise Exception('Failed to broadcast transaction')

    def broadcast_block(self, block: Block):
        for node in self.nodes:
            response = requests.post(
                f'http://{node}/block/new', json=asdict(block))
            if response.status_code != 201:
                raise Exception('Failed to broadcast block')
