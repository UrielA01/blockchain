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
