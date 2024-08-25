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
    def hash(self) -> str:
        block_as_dict = {
            'index': self.index,
            'merkle_root': self.merkle_root,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'timestamp': self.timestamp,
        }

        block_string = json.dumps(block_as_dict, sort_keys=True).encode()
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

    def __eq__(self, other: 'Block') -> bool:
        try:
            assert self.header == other.header
            assert self.transactions == other.transactions
            return True
        except AssertionError:
            return False