from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

from blockchain_utils.blockchain import Blockchain


class Node:
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain

    @staticmethod
    def validate_signature(public_key: bytes, signature: bytes, data: bytes) -> bool:
        public_key_object = RSA.import_key(public_key)
        hash_obj = SHA256.new(data)
        try:
            pkcs1_15.new(public_key_object).verify(hash_obj, signature)
            return True
        except (ValueError, TypeError):
            return False
