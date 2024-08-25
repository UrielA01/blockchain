import json
from typing import List

from src.utils.crypto_utils import calculate_sha256
from src.utils.io_mem_pool import get_transactions_from_memory, store_transactions_in_memory
from src.wallet.wallet import Wallet

def handle_transaction_data(data):
    if isinstance(data, str):
        return json.loads(data)

class TransactionInput:
    def __init__(self, transaction_hash: str, output_index: int, unlocking_script: str = ""):
        self.transaction_hash = transaction_hash
        self.output_index = output_index
        self.unlocking_script = unlocking_script

    def to_json(self, with_unlocking_script: bool = True) -> str:
        if with_unlocking_script:
            return json.dumps({
                "transaction_hash": self.transaction_hash,
                "output_index": self.output_index,
                "unlocking_script": self.unlocking_script
            })
        else:
            return json.dumps({
                "transaction_hash": self.transaction_hash,
                "output_index": self.output_index
            })

    @staticmethod
    def from_json(data: dict) -> 'TransactionInput':
        data = handle_transaction_data(data)
        transaction_hash = data['transaction_hash']
        output_index = data['output_index']
        unlocking_script = data['unlocking_script']
        return TransactionInput(transaction_hash, output_index, unlocking_script)


class TransactionOutput:
    def __init__(self, public_key_hash: bytes, amount: int):
        self.amount = amount
        self.public_key_hash = public_key_hash
        self.locking_script = (
            f"OP_DUP OP_HASH160 {public_key_hash} OP_EQUAL_VERIFY OP_CHECKSIG"
        )

    def to_json(self) -> str:
        return json.dumps({
            "amount": self.amount,
            "public_key_hash": self.public_key_hash,
            "locking_script": self.locking_script
        })

    @staticmethod
    def from_json(data: dict) -> 'TransactionOutput':
        data = handle_transaction_data(data)
        public_key_hash = data['public_key_hash']
        amount = data['amount']
        return TransactionOutput(public_key_hash, amount)


class Transaction:
    def __init__(self, inputs: List[TransactionInput], outputs: List[TransactionOutput]):
        self.inputs = inputs
        self.outputs = outputs

    @property
    def to_dict(self):
        return {
            "inputs": [tx_input.to_json() for tx_input in self.inputs],
            "outputs": [tx_output.to_json() for tx_output in self.outputs],
        }

    @property
    def to_dict_no_script(self):
        return {
            "inputs": [tx_input.to_json(with_unlocking_script=False) for tx_input in self.inputs],
            "outputs": [tx_output.to_json() for tx_output in self.outputs],
        }

    @property
    def hash(self):
        transaction_bytes = json.dumps(
            self.to_dict_no_script, indent=2).encode('utf-8')
        return calculate_sha256(transaction_bytes)

    def sign_transaction_data(self, owner: Wallet):
        transaction_bytes = json.dumps(self.to_dict_no_script).encode('utf-8')
        signature = Wallet.convert_signature_to_str(
            owner.sign(transaction_bytes))
        return signature

    def sign_inputs(self, owner: Wallet):
        signature = self.sign_transaction_data(owner)
        for transaction_input in self.inputs:
            transaction_input.unlocking_script = f"{signature} {owner.public_key_hex}"

    @staticmethod
    def from_json(data: str | dict) -> 'Transaction':
        inputs = [TransactionInput.from_json(input_data) for input_data in data['inputs']]
        outputs = [TransactionOutput.from_json(output_data) for output_data in data['outputs']]
        return Transaction(inputs, outputs)

    def store(self):
        current_transactions = get_transactions_from_memory()
        current_transactions.append(self.to_dict)
        store_transactions_in_memory(current_transactions)

    def send_to_nodes(self) -> dict:
        return {
            "inputs": [i.to_json() for i in self.inputs],
            "outputs": [i.to_json() for i in self.outputs],
        }
