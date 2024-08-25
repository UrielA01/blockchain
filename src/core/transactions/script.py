from src.utils.crypto_utils import calculate_sha256, calculate_ripemd160
from src.wallet.wallet import Wallet


class Stack:
    def __init__(self):
        self.elements = []

    def push(self, element):
        self.elements.append(element)

    def pop(self):
        return self.elements.pop()


class StackScript(Stack):
    def __init__(self, transaction_bytes: bytes):
        super().__init__()
        self.transaction_bytes = transaction_bytes

    def op_dup(self):
        public_key = self.pop()
        self.push(public_key)
        self.push(public_key)

    def op_hash160(self):
        public_key = self.pop()
        self.push(calculate_ripemd160(calculate_sha256(public_key)))

    def op_equalverify(self):
        last_element = self.pop()
        second_last_element = self.pop()
        if not last_element == second_last_element:
            raise ValueError("Invalid hash")

    def op_checksig(self):
        public_key = self.pop()
        signature = self.pop()
        public_key_bytes = public_key.encode("utf-8")
        if not Wallet.valid_signature(signature, public_key_bytes, self.transaction_bytes):
            raise ValueError("Invalid signature")


    def execute(self, script: str):
        for element in script:
            if element.startswith("OP"):
                class_method = getattr(StackScript, element.lower())
                class_method(self)
            else:
                self.push(element)
