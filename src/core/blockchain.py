import json
from dataclasses import dataclass, field
from typing import List, Set

from src.core.block import Block, BlockHeader
from src.core.consensus import Consensus
from src.core.merkle_tree import MerkleTree
from src.core.new_block.new_block import NewBlock
from src.core.transaction import Transaction
from src.utils.io_mem_pool import get_transactions_from_memory

class BlockchainException(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


@dataclass
class Blockchain:
    last_block: Block = field(default_factory=lambda: Block(
        header=BlockHeader(index=1),
        transactions=[],
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
            transactions=[transaction],
            previous_block=self.last_block,
        )
        self.last_block = new_block
        self.length += 1
        return new_block

    def create_new_block(self):
        transactions = get_transactions_from_memory()
        merkle_tree = MerkleTree([json.dumps(tx).encode('utf-8') for tx in transactions])
        if transactions:
            block_header = BlockHeader(
                index=self.length + 1,
                merkle_root=merkle_tree.root,
                previous_hash= self.last_block.header.hash,
            )
            block_header.nonce = NewBlock.set_nonce(block_header)
            transactions_list = [Transaction.from_json(transaction) for transaction in transactions]
            new_block = Block(transactions=transactions_list, header=block_header)
            self.last_block = new_block
            self.length += 1
        else:
            raise BlockchainException("", "No transaction in mem_pool.json")

