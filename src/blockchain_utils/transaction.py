from dataclasses import dataclass, field
import time

from utils.crypto_utils import calculate_sha256
from wallet import Wallet


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
