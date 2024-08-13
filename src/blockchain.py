from dataclasses import asdict, dataclass, field
import hashlib
import json
import time
from typing import List, Set
from urllib.parse import urlparse
import requests


@dataclass
class Transaction:
    sender: str
    recipient: str
    amount: int

    def __repr__(self):
        return f"{self.sender} -> {self.recipient}: {self.amount}"

    def valid_transaction(self) -> bool:
        return self.amount > 0 and self.sender and self.recipient


@dataclass
class Block:
    index: int
    timestamp: float
    transactions: List[Transaction]
    previous_hash: str
    nonce: int = None
    hash: str = None

    def __post_init__(self):
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        """
        Creates a SHA-256 hash of the block's contents using the dataclass dictionary representation.
        :return: <str> Hash of the block
        """
        block_as_dict = asdict(self)
        block_as_dict.pop('hash', None)

        # Convert the block's data to a dictionary, sort keys, and dump as JSON string
        block_string = json.dumps(block_as_dict, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


@dataclass
class Blockchain:
    chain: List[Block] = field(default_factory=list)
    current_transactions: List[Transaction] = field(default_factory=list)
    nodes: Set[str] = field(default_factory=set)

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
        nonce = self.proof_of_work(block)
        block.nonce = nonce
        block.hash = block.compute_hash()
        self.current_transactions = []
        self.chain.append(block)

        self.broadcast_block(block)
        return block

    def recive_block(self, block: Block) -> bool:
        new_chain = self.chain.copy()
        new_chain.append(block)

        if self.valid_chain(new_chain):
            self.chain = new_chain
            return True

        return False

    def new_transaction(self, sender: str, recipient: str, amount: int) -> int:
        transaction = Transaction(sender, recipient, amount)

        if not transaction.valid_transaction():
            raise ValueError("Invalid transaction")

        self.current_transactions.append(transaction)

        self.broadcast_transaction(transaction)

        return self.last_block.index + 1

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def valid_nonce(self, block: Block, nonce: int) -> bool:
        block.nonce = nonce
        return block.compute_hash()[:4] == "0000"

    def proof_of_work(self, block: Block) -> int:
        """
        Simple Proof of Work Algorithm:
        Find a nonce such that the hash of the block contains leading 4 zeros.
        :param last_block: <Block> Last block in the chain
        :return: <int> The valid nonce
        """
        nonce = 0
        while True:
            if self.valid_nonce(block, nonce):
                return nonce
            nonce += 1

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

    def valid_chain(self, chain: List[Block]) -> bool:
        # Determine if a given blockchain is valid
        previous_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            current_block = chain[current_index]

            # Check that the hash of the block is correct
            if current_block.previous_hash != previous_block.compute_hash():
                print("Invalid previous hash")
                return False

            # Check that the Proof of Work is correct
            if not self.valid_nonce(current_block, current_block.nonce):
                print("Invalid PoW")
                return False

            previous_block = current_block
            current_index += 1

        return True

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
                if length > max_length and self.valid_chain(chain):
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
                f'http://{node}/transactions/new', json=asdict(transaction))
            if response.status_code != 201:
                raise Exception('Failed to broadcast transaction')

    def broadcast_block(self, block: Block):
        for node in self.nodes:
            response = requests.post(
                f'http://{node}/block/new', json=asdict(block))
            if response.status_code != 201:
                raise Exception('Failed to broadcast block')
