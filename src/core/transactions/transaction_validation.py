from src.core.blockchain import Blockchain
from src.core.transactions.script import StackScript
from src.core.transactions.transaction import Transaction

import json


class TransactionValidation:
    def __init__(self, blockchain: Blockchain, transaction: Transaction):
        self.blockchain = blockchain
        self.transaction = transaction

    def get_transaction_from_utxo(self, tx_hash: str) -> Transaction:
        current_block = self.blockchain.last_block
        while current_block:
            found_transaction = current_block.find_transaction_by_hash(tx_hash)
            if found_transaction:
                return found_transaction
            current_block = current_block.previous_block

    def get_locking_script_from_utxo(self, utxo_hash: str, utxo_index: int):
        transaction = self.get_transaction_from_utxo(utxo_hash)
        return transaction.outputs[utxo_index].locking_script

    def get_total_amount_in_inputs(self) -> int:
        total_in = 0
        for tx_input in self.transaction.inputs:
            transaction = self.get_transaction_from_utxo(
                tx_input.transaction_hash)
            utxo_amount = transaction.outputs[tx_input.output_index].amount
            total_in = total_in + utxo_amount
        return total_in

    def get_total_amount_in_outputs(self) -> int:
        total_out = 0
        for tx_output in self.transaction.outputs:
            amount = tx_output.amount
            total_out = total_out + amount
        return total_out

    def validate_funds(self):
        assert self.get_total_amount_in_inputs() == self.get_total_amount_in_outputs()

    def validate(self):
        for tx_input in self.transaction.inputs:
            locking_script = self.get_locking_script_from_utxo(
                tx_input.transaction_hash, tx_input.output_index)
            transaction_bytes = json.dumps(
            self.transaction.to_dict, indent=2).encode('utf-8')
            unlock_stack_script = StackScript(tx_input.unlocking_script, transaction_bytes)
            lock_stack_script = StackScript(locking_script, transaction_bytes)
            unlock_stack_script.execute()
            lock_stack_script.execute()

