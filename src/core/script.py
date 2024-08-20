import binascii
import json

from Crypto.PublicKey import RSA

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
    def __init__(self, transaction_data: dict):
        super().__init__()
        for count, tx_input in enumerate(transaction_data["inputs"]):
            tx_input_dict = json.loads(tx_input)
            tx_input_dict.pop("unlocking_script")
            transaction_data["inputs"][count] = json.dumps(tx_input_dict)
        self.transaction_data = transaction_data

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
        assert last_element == second_last_element

    def op_checksig(self):
        public_key = self.pop()
        signature = self.pop()
        public_key_bytes = public_key.encode("utf-8")
        transaction_bytes = json.dumps(
            self.transaction_data, indent=2).encode('utf-8')
        Wallet.valid_signature(signature, public_key_bytes, transaction_bytes)
