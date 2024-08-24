from dataclasses import dataclass, field
from typing import List, Set

from src.core.block import Block, BlockHeader
from src.core.consensus import Consensus
from src.core.transaction import Transaction


@dataclass
class Blockchain:
    last_block: Block = field(default_factory=lambda: Block(
        header=BlockHeader(index=1),
        transactions=Transaction(None, [], []),
    ))
    length: int = 1
    current_transactions: List[Transaction] = field(default_factory=list)
    nodes: Set[str] = field(default_factory=set)
    consensus: Consensus = field(default_factory=Consensus)

    def add_new_block(self, transaction: Transaction):
        new_block_header = BlockHeader(
            index=self.length + 1,
            previous_hash=self.last_block.header.hash
        )
        new_block = Block(
            header=new_block_header,
            transactions=transaction,
            previous_block=self.last_block,
        )
        self.last_block = new_block
        self.length += 1
        return new_block
