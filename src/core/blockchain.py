import json
from dataclasses import dataclass, field
from typing import List, Set

from src.core.blocks.block import Block, BlockHeader
from src.core.merkle_tree import MerkleTree
from src.core.transactions.transaction import Transaction
from src.utils.io_mem_pool import get_transactions_from_memory
from src.wallet.wallet import Wallet


class BlockchainException(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


@dataclass
class Blockchain:
    wallet: Wallet
    last_block: Block = field(default_factory=lambda: Block(
        header=BlockHeader(index=1),
        transactions=[],
    ))
    length: int = 1
    current_transactions: List[Transaction] = field(default_factory=list)
    nodes: Set[str] = field(default_factory=set)

    def add_new_block_d(self, transaction: Transaction):
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

    def add_new_block(self, new_block: Block):
        new_block.previous_block = self.last_block
        self.last_block = new_block
        self.length += 1
        return new_block

    def get_transaction_from_utxo(self, tx_hash: str) -> Transaction:
        current_block = self.last_block
        while current_block:
            found_transaction = current_block.find_transaction_by_hash(tx_hash)
            if found_transaction:
                return found_transaction
            current_block = current_block.previous_block

    def get_transaction_fees(self, transactions: List[Transaction]) -> float:
        transaction_fees = 0
        for transaction in transactions:
            input_amount = 0
            output_amount = 0
            for transaction_input in transaction.inputs:
                utxo = self.get_transaction_from_utxo(transaction_input.transaction_hash)
                if utxo:
                    utxo_amount = utxo.outputs[transaction_input.output_index].amount
                    input_amount = input_amount + utxo_amount
            for transaction_output in transaction.outputs:
                output_amount = output_amount + transaction_output.amount
            transaction_fees = transaction_fees + (input_amount-output_amount)
        return transaction_fees

    def create_new_block(self):
        from src.core.blocks.block_validation import ProofOfWork
        transactions = get_transactions_from_memory()
        if transactions:
            transactions = [Transaction.from_json(transaction) for transaction in transactions]
            transaction_fees = self.get_transaction_fees(transactions)
            coinbase_transaction = ProofOfWork.get_coin_base_transaction(transaction_fees, miner_wallet=self.wallet)
            transactions.append(coinbase_transaction)
            merkle_tree = MerkleTree([json.dumps(tx.to_dict_no_script).encode('utf-8') for tx in transactions])
            block_header = BlockHeader(
                index=self.length + 1,
                merkle_root=merkle_tree.root,
                previous_hash=self.last_block.header.hash,
            )
            block_header.nonce = ProofOfWork.find_nonce(block_header)
            new_block = Block(transactions=transactions, header=block_header)
            self.last_block = new_block
            self.length += 1
        else:
            raise BlockchainException("", "No transaction in mem_pool.json")
