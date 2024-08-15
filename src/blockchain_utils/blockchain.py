from dataclasses import asdict, dataclass, field
import time
from typing import List, Set
from urllib.parse import urlparse
import requests

from blockchain_utils.block import Block
from blockchain_utils.consensus import Consensus
from blockchain_utils.transaction import Transaction


@dataclass
class Blockchain:
    chain: List[Block] = field(default_factory=list)
    current_transactions: List[Transaction] = field(default_factory=list)
    nodes: Set[str] = field(default_factory=set)
    consensus: Consensus = field(default_factory=Consensus)

    def __post_init__(self):
        genesis_block = Block(
            index=1,
            timestamp=time.time(),
            transactions=[],
            previous_hash=None
        )
        self.chain.append(genesis_block)

    def add_block(self, previous_hash: str) -> Block:
        block = Block(
            index=len(self.chain) + 1,
            timestamp=time.time(),
            transactions=self.current_transactions,
            previous_hash=previous_hash
        )
        nonce = self.consensus.proof_of_work(block)
        block.nonce = nonce
        block.hash = block.compute_hash()
        self.current_transactions = []
        self.chain.append(block)

        self.broadcast_block(block)
        return block

    def receive_block(self, block: Block) -> bool:
        new_chain = self.chain.copy()
        new_chain.append(block)

        if self.consensus.valid_chain(new_chain):
            self.chain = new_chain
            return True

        return False

    def new_transaction(self, transaction: Transaction) -> int:
        timestamps = [
            transaction.timestamp for transaction in self.current_transactions]
        if transaction.timestamp in timestamps:
            raise Exception("Transaction already exists")
        self.current_transactions.append(transaction)
        return self.last_block.index + 1

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

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

    def resolve_conflicts(self) -> bool:
        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """
        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()["length"]
                chain_data = response.json()["chain"]

                # Rebuild the chain using the Block dataclass
                chain = [
                    Block(
                        index=block['index'],
                        timestamp=block['timestamp'],
                        transactions=block['transactions'],
                        nonce=block['nonce'],
                        previous_hash=block['previous_hash'],
                    ) for block in chain_data
                ]

                # Check if the length is longer and the chain is valid
                if length > max_length and self.consensus.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

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
