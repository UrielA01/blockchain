from src.core.blockchain import Blockchain
from src.core.transactions.script import StackScript
from src.core.transactions.transaction import Transaction

import json

from src.utils.consts import MINER_REWARD


class TransactionException(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)
        self.message = message

    def __str__(self):
        return self.message

class TransactionValidation:
    def __init__(self, blockchain: Blockchain, transaction: Transaction):
        self.blockchain = blockchain
        self.transaction = transaction

    def get_locking_script_from_utxo(self, utxo_hash: str, utxo_index: int):
        transaction = self.blockchain.get_transaction_from_utxo(utxo_hash)
        if transaction is None:
            raise TransactionException("UTXO not found")
        return transaction.outputs[utxo_index].locking_script

    def get_total_amount_in_inputs(self) -> int:
        total_in = 0
        for tx_input in self.transaction.inputs:
            transaction = self.blockchain.get_transaction_from_utxo(
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
        total_inputs = self.get_total_amount_in_inputs()
        total_outputs = self.get_total_amount_in_outputs()
        if self.transaction.is_coin_base:
            empty_inputs = total_inputs == 0
            output_with_miner_reward = total_outputs >= MINER_REWARD
            if not (empty_inputs or output_with_miner_reward):
                raise TransactionException("Invalid coinbase transaction")
        else:
            if not total_inputs >= total_outputs:
                raise TransactionException("Invalid transaction funds")

    def validate_scripts(self):
        try:
            for tx_input in self.transaction.inputs:
                locking_script = self.get_locking_script_from_utxo(
                    tx_input.transaction_hash, tx_input.output_index)
                unlocking_script = tx_input.unlocking_script
                transaction_bytes = json.dumps(
                self.transaction.to_dict_no_script, indent=2).encode('utf-8')
                stack_script = StackScript(transaction_bytes)
                stack_script.execute(unlocking_script)
                stack_script.execute(locking_script)
        except (ValueError, TransactionException) as e:
            print(e)
            raise TransactionException(f'Invalid transaction inputs - {e}')

    def validate(self):
        self.validate_funds()
        self.validate_scripts()