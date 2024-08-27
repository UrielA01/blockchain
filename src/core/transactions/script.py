from src.utils.crypto_utils import calculate_sha256, calculate_ripemd160
from src.wallet.wallet import Wallet

import binascii

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
        """
            Duplicates the top element of the stack.

            Pops the top element (e.g., a public key) from the stack,
            and then pushes it back onto the stack twice, resulting in two identical elements at the top.
        """
        public_key = self.pop()
        self.push(public_key)
        self.push(public_key)

    def op_hash160(self):
        """
            Hashes the top element of the stack twice (SHA-256 followed by RIPEMD-160).

            Pops the top element (e.g., a public key) from the stack,
            computes its SHA-256 hash, then its RIPEMD-160 hash, and pushes the result back onto the stack.
        """
        public_key = self.pop()
        self.push(calculate_ripemd160(calculate_sha256(public_key)))

    def op_equalverify(self):
        """
            Verifies that the top two elements of the stack are equal.

            Pops the top two elements from the stack and checks if they are identical.
            If they are not equal, it raises a ValueError, indicating an invalid transaction.
        """
        last_element = self.pop()
        second_last_element = self.pop()
        if not last_element == second_last_element:
            raise ValueError("Invalid hash")

    def op_checksig(self):
        """
            Verifies a digital signature using the public key and transaction data.

            Pops the top two elements from the stack: the first is assumed to be a public key,
            and the second a digital signature. The method verifies the signature against the transaction bytes
            using the provided public key. If the signature is invalid, it raises a ValueError.
        """

        public_key = self.pop()
        signature = self.pop()
        public_key_bytes = public_key.encode("utf-8")
        if not Wallet.valid_signature(binascii.unhexlify(signature), public_key_bytes, self.transaction_bytes):
            raise ValueError("Invalid signature")


    def execute(self, script: str):
        """
            Executes a given script by interpreting each element.

            Iterates over each element in the script string. If the element is an operation (starting with 'OP'),
            it dynamically calls the corresponding method in the StackScript class. Otherwise, it pushes the element onto the stack.
        """
        script = script.split(" ")
        for element in script:
            if element.startswith("OP"):
                class_method = getattr(StackScript, element.lower())
                class_method(self)
            else:
                self.push(element)
