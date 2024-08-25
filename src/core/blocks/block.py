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
    nonce: int = None
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
        try:
            assert self.previous_hash == other.previous_hash
            assert self.merkle_root == other.merkle_root
            assert self.timestamp == other.timestamp
            assert self.nonce == other.nonce
            assert self.hash == other.hash
            return True
        except AssertionError:
            return False


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
            'header': self.header.to_dict,
            'transactions': [tx.to_dict for tx in self.transactions],
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
        try:
            assert self.header == other.header
            assert self.transactions == other.transactions
            return True
        except AssertionError:
            return False