import json
import time
from dataclasses import dataclass, field
from typing import List

from src.core.transactions.transaction import Transaction
from src.utils.crypto_utils import calculate_sha256

@dataclass
class BlockHeader:
    index: int
    previous_hash: str = None
    merkle_root: str = None
    nonce: int = 0
    timestamp: float = field(default_factory=lambda: time.time())

    @property
    def to_dict(self) -> dict:
        return {
            'index': self.index,
            'merkle_root': self.merkle_root,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'timestamp': self.timestamp,
        }

    @staticmethod
    def from_json(block_header: dict) -> 'BlockHeader':
        return BlockHeader(block_header['index'], block_header['previous_hash'], block_header['merkle_root'], block_header['nonce'], block_header['timestamp'])

    @property
    def hash(self) -> str:
        block_string = json.dumps(self.to_dict, sort_keys=True).encode()
        return calculate_sha256(block_string)

    def __eq__(self, other: 'BlockHeader') -> bool:
        return (
            self.previous_hash == other.previous_hash and
            self.merkle_root == other.merkle_root and
            self.timestamp == other.timestamp and
            self.nonce == other.nonce and
            self.hash == other.hash
        )


@dataclass
class Block:
    header: BlockHeader
    transactions: List[Transaction]
    previous_block: 'Block' = None

    def find_transaction_by_hash(self, tx_hash) -> Transaction:
        for transaction in self.transactions:
            if transaction.hash == tx_hash:
                return transaction

    @property
    def to_dict(self) -> dict:
        return {
            'header': {**self.header.to_dict, 'hash': self.header.hash},
            'transactions': [{**tx.to_dict, "hash": tx.hash} for tx in self.transactions],
        }

    @staticmethod
    def from_json(block: dict) -> 'Block':
        """
            previous block is add when the block is added to blockchain
        """
        header = BlockHeader.from_json(block['header'])
        transactions = [Transaction.from_json(transaction) for transaction in block['transactions']]
        return Block(header, transactions)

    def __eq__(self, other: 'Block') -> bool:
        return (
            self.header == other.header and
            self.transactions == other.transactions
        )