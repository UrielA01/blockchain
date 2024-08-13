from dataclasses import dataclass


@dataclass
class Transaction:
    sender: str
    recipient: str
    amount: int

    def __repr__(self):
        return f"{self.sender} -> {self.recipient}: {self.amount}"

    def valid_transaction(self) -> bool:
        return self.amount > 0 and self.sender and self.recipient
