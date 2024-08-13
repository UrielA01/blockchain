from dataclasses import asdict, dataclass
import hashlib
import json
from typing import List

from transaction import Transaction


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
