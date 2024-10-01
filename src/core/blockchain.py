import copy
import json
from dataclasses import dataclass, field
from typing import List

from src.core.blocks.block import Block, BlockHeader
from src.core.merkle_tree import MerkleTree
from src.core.transactions.transaction import Transaction
from src.utils.io_mem_pool import get_transactions_from_memory, reset_transaction_memory
from src.wallet.wallet import Wallet


class BlockchainException(Exception):
    pass


@dataclass
class Blockchain:
    wallet: Wallet
    last_block: Block = field(default_factory=lambda: Block(
        header=BlockHeader(index=1),
        transactions=[],
    ))
    length: int = 1

    def __post_init__(self):
        from src.core.blocks.block_validation import ProofOfWork
        if self.last_block:
            genesis_nonce = ProofOfWork.find_nonce(self.last_block.header)
            self.last_block.header.nonce = genesis_nonce

    def add_new_block(self, new_block: Block):
        from src.core.blocks.block_validation import BlockValidation, BlockException
        from src.core.transactions.transaction_validation import TransactionValidationException
        try:
            validate_block = BlockValidation(blockchain=self, block=new_block)
            validate_block.validate()
            new_block.previous_block = self.last_block
            self.last_block = new_block
            self.length += 1
            return new_block
        except (BlockException, TransactionValidationException) as e:
            print(e)
            raise BlockchainException("", "Invalid blockchain")

    def get_transaction_from_utxo(self, tx_hash: str) -> Transaction:
        current_block = self.last_block
        while current_block:
            found_transaction = current_block.find_transaction_by_hash(tx_hash)
            if found_transaction:
                return copy.deepcopy(found_transaction)
            current_block = current_block.previous_block
        from src.core.transactions.transaction_validation import TransactionValidationException
        raise TransactionValidationException("UTXO not found")

    def get_transaction_fees(self, transactions: List[Transaction]) -> float:
        transaction_fees = 0
        for transaction in transactions:
            input_amount = 0
            output_amount = 0
            for transaction_input in transaction.inputs:
                utxo = self.get_transaction_from_utxo(
                    transaction_input.transaction_hash)
                if utxo:
                    utxo_amount = utxo.outputs[transaction_input.output_index].amount
                    input_amount = input_amount + utxo_amount
            for transaction_output in transaction.outputs:
                output_amount = output_amount + transaction_output.amount
            transaction_fees = transaction_fees + (input_amount-output_amount)
        return transaction_fees

    def create_new_block(self, transactions: List[Transaction] = None):
        from src.core.blocks.block_validation import ProofOfWork
        if transactions is None:
            transactions = get_transactions_from_memory()
            transactions = [Transaction.from_json(
                transaction) for transaction in transactions]
        from src.core.transactions.transaction_validation import TransactionValidation, TransactionValidationException
        valid_transactions = []
        for transaction in transactions:
            try:
                validate = TransactionValidation(
                    transaction=transaction, blockchain=self)
                validate.validate()
                valid_transactions.append(transaction)
            except TransactionValidationException as e:
                print(f"Transaction validation failed: {e}")
                print("Skipping")
        if len(valid_transactions) == 0:
            print("Warning: Transaction list is empty")
        transaction_fees = self.get_transaction_fees(valid_transactions)
        coinbase_transaction = ProofOfWork.get_coin_base_transaction(
            transaction_fees, miner_wallet=self.wallet)
        valid_transactions.append(coinbase_transaction)
        merkle_tree = MerkleTree(
            [json.dumps(tx.to_dict_no_script).encode('utf-8') for tx in valid_transactions])
        block_header = BlockHeader(
            index=self.length + 1,
            merkle_root=merkle_tree.root.value,
            previous_hash=self.last_block.header.hash,
        )
        nonce = ProofOfWork.find_nonce(block_header)
        block_header.nonce = nonce
        new_block = Block(transactions=valid_transactions, header=block_header)
        self.add_new_block(new_block)
        reset_transaction_memory()
        return new_block

    def get_block_by_hash(self, hash: str):
        current_block = self.last_block
        while current_block:
            if current_block.header.hash == hash:
                return current_block
            current_block = current_block.previous_block
        return None

    @staticmethod
    def from_json_list(blockchain_dict: List[dict], wallet: Wallet):
        try:
            # The blockchain comes with the genesis block at the end due to the linked list nature
            new_blockchain = Blockchain(wallet, None, 0)
            for block in reversed(blockchain_dict):
                block = Block.from_json(block)
                new_blockchain.add_new_block(block)
            return new_blockchain
        except BlockchainException:
            print("Received invalid blockchain")
            return None
