from dataclasses import dataclass, field
import hashlib
import json
import time
from typing import List, Set
from urllib.parse import urlparse
import requests


@dataclass
class Block:
    index: int
    timestamp: float
    transactions: list
    proof: int
    previous_hash: str


@dataclass
class Blockchain:
    chain: List[Block] = field(default_factory=list)
    current_transactions: List[dict] = field(default_factory=list)
    nodes: Set[str] = field(default_factory=set)

    def __post_init__(self):
        genesis_block = Block(
            index=1,
            timestamp=time.time(),
            transactions=[],
            proof=100,
            previous_hash=1
        )
        self.chain.append(genesis_block)

    def new_block(self, proof: int, previous_hash: str = None) -> Block:
        previous_hash = previous_hash or self.hash(self.chain[-1])
        block = Block(
            index=len(self.chain) + 1,
            timestamp=time.time(),
            transactions=self.current_transactions,
            proof=proof,
            previous_hash=previous_hash
        )
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender: str, recipient: str, amount: int) -> int:
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block.index + 1

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    @staticmethod
    def hash(block: Block) -> str:
        block_string = json.dumps(block.__dict__, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof: int) -> int:
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def register_node(self, address: str) -> None:
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain: List[Block]) -> bool:
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            current_block = chain[current_index]
            print(f'{last_block}')
            print(f'{current_block}')
            print("\n-----------\n")

            # Check that the hash of the block is correct
            if current_block.previous_hash != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block.proof, current_block.proof):
                return False

            last_block = current_block
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
                        proof=block['proof'],
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
