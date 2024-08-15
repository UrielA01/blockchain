from Crypto.Hash import RIPEMD160
import hashlib
from Crypto.PublicKey import RSA
import base58

from utils.crypto_utils import calculate_ripemd160, calculate_sha256


class Wallet:
    def __init__(self):
        self.private_key, self.public_key = initialize_wallet()
        self.address = base58.b58encode(
            hash_address(self.public_key))


def initialize_wallet():
    private_key = RSA.generate(2048)
    public_key = private_key.publickey().export_key()
    return private_key, public_key


def hash_address(key: bytes) -> str:
    first_hash = calculate_sha256(key)
    first_hash = bytearray(first_hash, "utf-8")
    return calculate_ripemd160(first_hash)
