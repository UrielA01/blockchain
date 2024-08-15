from dataclasses import dataclass, field
import time


@dataclass
class Transaction:
    sender: str
    recipient: str
    amount: int
    timestamp: float = field(default_factory=lambda: time.time())

    def __repr__(self):
        return f"{self.sender} -> {self.recipient}: {self.amount}"

    def valid_transaction(self) -> bool:
        return self.amount > 0 and self.sender and self.recipient

    def as_dict(self):
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp
        }

    def convert_to_bytes(self) -> bytes:
        return str(self.as_dict()).encode('utf-8')
