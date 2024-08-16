import binascii
from dataclasses import dataclass, field
import json
import time
from typing import List

from utils.crypto_utils import calculate_sha256
from wallet import Wallet


class TransactionInput:
    def __init__(self, transaction_hash: str, output_index: int, public_key: str = "", signature: str = ""):
        self.transaction_hash = transaction_hash
        self.output_index = output_index
        self.public_key = public_key
        self.signature = signature

    def to_json(self, include_signature: bool = True, include_public_key: bool = True) -> dict:
        return {
            "transaction_hash": self.transaction_hash,
            "output_index": self.output_index,
            "public_key": self.public_key if include_public_key else "",
            "signature": self.signature if include_signature else ""
        }

    def __repr__(self):
        return f"{self.transaction_hash}:{self.output_index}"


class TransactionOutput:
    def __init__(self, public_key_hash: str, amount: int):
        self.amount = amount
        self.public_key_hash = public_key_hash

    def to_json(self) -> dict:
        return {
            "amount": self.amount,
            "public_key_hash": self.public_key_hash
        }


@dataclass
class Transaction:
    owner: Wallet
    inputs: List[TransactionInput]
    outputs: List[TransactionOutput]
    timestamp: float = field(default_factory=lambda: time.time())

    def valid_transaction(self) -> bool:
        return self.amount > 0 and self.owner and self.recipient

    def tx_data_as_dict(self):
        return {
            "inputs": [tx_input.to_json(include_signature=False, include_public_key=False) for tx_input in self.inputs],
            "outputs": [tx_output.to_json() for tx_output in self.outputs],
            "timestamp": self.timestamp,
        }

    def sign_transaction_data(self):
        transaction_dict = self.tx_data_as_dict()
        transaction_bytes = json.dumps(transaction_dict).encode('utf-8')
        hash = calculate_sha256(transaction_bytes)
        signature = Wallet.convert_signature_to_str(self.owner.sign(hash))
        return signature

    def __post_init__(self):
        self.signature = Wallet.convert_signature_to_str(
            self.owner.sign(self.convert_to_bytes()))

    def sign(self):
        signature_hex = binascii.hexlify(
            self.sign_transaction_data()).decode("utf-8")
        for transaction_input in self.inputs:
            transaction_input.signature = signature_hex
            transaction_input.public_key = self.owner.public_key
