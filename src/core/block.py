import json
import time
from dataclasses import dataclass, field

from src.core.transaction import Transaction
from src.utils.crypto_utils import calculate_sha256


@dataclass
class Block:
    index: int
    transaction_data: Transaction
    previous_hash: str
    previous_block: 'Block'
    timestamp: float = field(default_factory=lambda: time.time())
    nonce: int = None

    @property
    def transaction_hash(self) -> str:
        transaction_bytes = json.dumps(
            self.transaction_data.as_dict, indent=2).encode('utf-8')
        return calculate_sha256(transaction_bytes)

    @property
    def hash(self) -> str:
        """
        Creates a SHA-256 hash of the block's contents using the dataclass dictionary representation.
        :return: <str> Hash of the block
        """
        block_as_dict = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transaction_data.as_dict,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }

        # Convert the block's data to a dictionary, sort keys, and dump as JSON string
        block_string = json.dumps(block_as_dict, sort_keys=True).encode()
        return calculate_sha256(block_string)
