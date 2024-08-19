from dataclasses import asdict, dataclass
import json
from typing import List

from .transaction import Transaction
from utils.crypto_utils import calculate_sha256


@dataclass
class Block:
    index: int
    timestamp: float
    transaction_data: Transaction
    previous_hash: str
    previous_block: 'Block'
    nonce: int = None
    hash: str = None

    def __post_init__(self):
        self.hash = self.compute_hash()

    @property
    def transaction_hash(self) -> str:
        transaction_bytes = json.dumps(
            self.transaction_data.tx_data_as_dict(), indent=2).encode('utf-8')
        return calculate_sha256(transaction_bytes)

    def compute_hash(self) -> str:
        """
        Creates a SHA-256 hash of the block's contents using the dataclass dictionary representation.
        :return: <str> Hash of the block
        """
        block_as_dict = asdict(self)
        block_as_dict.pop('hash', None)
        block_as_dict.pop('previous_block', None)

        # Convert the block's data to a dictionary, sort keys, and dump as JSON string
        block_string = json.dumps(block_as_dict, sort_keys=True).encode()
        return calculate_sha256(block_string)
