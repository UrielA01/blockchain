import hashlib
from Crypto.Hash import RIPEMD160


def calculate_sha256(data: str | bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def calculate_ripemd160(data: str) -> str:
    hash = RIPEMD160.new()
    hash.update(data)
    return hash.hexdigest()
