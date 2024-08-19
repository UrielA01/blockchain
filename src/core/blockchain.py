import time
from dataclasses import asdict, dataclass, field
from typing import List, Set
from urllib.parse import urlparse

import requests

from src.core.block import Block
from src.core.consensus import Consensus
from src.core.transaction import Transaction


@dataclass
class Blockchain:
    last_block: Block = field(default_factory=lambda: Block(
        index=1,
        timestamp=time.time(),
        transaction_data=Transaction(None, [], []),
        previous_hash=None,
        previous_block=None
    ))
    length: int = 1
    current_transactions: List[Transaction] = field(default_factory=list)
    nodes: Set[str] = field(default_factory=set)
    consensus: Consensus = field(default_factory=Consensus)

    def add_new_block(self, transaction: Transaction):
        new_block = Block(
            index=len(self.current_transactions) + 1,
            transaction_data=transaction,
            previous_hash=self.last_block.hash,
            previous_block=self.last_block,
        )
        self.last_block = new_block
        return new_block
