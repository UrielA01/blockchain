from dataclasses import dataclass, field
import time

from utils.crypto_utils import calculate_sha256
from wallet import Wallet


class TransactionInput:
    def __init__(self, transaction_hash: str, output_index: int, public_key: str = "", signature: str = ""):
        self.transaction_hash = transaction_hash
        self.output_index = output_index
        self.public_key = public_key
        self.signature = signature

    def to_json(self, include_signature: bool = False) -> dict:
        return {
            "transaction_hash": self.transaction_hash,
            "output_index": self.output_index,
            "public_key": self.public_key,
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
    sender: Wallet
    recipient: bytes
    amount: int
    timestamp: float = field(default_factory=lambda: time.time())
    signature: str = None

    def __repr__(self):
        return f"{self.sender.address} -> {self.recipient}: {self.amount}"

    def valid_transaction(self) -> bool:
        return self.amount > 0 and self.sender and self.recipient

    def as_dict(self):
        return {
            "sender": self.sender.address,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "signature": self.signature
        }

    def convert_to_bytes(self) -> bytes:
        return str(self.as_dict()).encode('utf-8')

    def __post_init__(self):
        self.signature = Wallet.convert_signature_to_str(
            self.sender.sign(self.convert_to_bytes()))
