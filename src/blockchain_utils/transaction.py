import binascii
from dataclasses import dataclass, field
import json
import time
from typing import List

from utils.crypto_utils import calculate_sha256
from wallet import Wallet


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


class TransactionOutput:
    def __init__(self, public_key_hash: bytes, amount: int):
        self.amount = amount
        self.locking_script = (
            f"OP_DUP OP_HASH160 {public_key_hash} OP_EQUAL_VERIFY OP_CHECKSIG"
        )

    def to_json(self) -> str:
        return json.dumps({
            "amount": self.amount,
            "locking_script": self.locking_script
        })


@dataclass
class Transaction:
    owner: Wallet
    inputs: List[TransactionInput]
    outputs: List[TransactionOutput]

    def tx_data_as_dict(self):
        return {
            "inputs": [tx_input.to_json(include_signature=False, include_public_key=False) for tx_input in self.inputs],
            "outputs": [tx_output.to_json() for tx_output in self.outputs],
        }

    def sign_transaction_data(self):
        transaction_dict = self.tx_data_as_dict()
        transaction_bytes = json.dumps(transaction_dict).encode('utf-8')
        signature = Wallet.convert_signature_to_str(
            self.owner.sign(transaction_bytes))
        return signature

    def sign_inputs(self):
        signature = self.sign_transaction_data()
        for transaction_input in self.inputs:
            transaction_input.signature = signature
            transaction_input.public_key = self.owner.public_key

    def send_to_nodes(self) -> dict:
        return {
            "inputs": [i.to_json() for i in self.inputs],
            "outputs": [i.to_json() for i in self.outputs],
        }
