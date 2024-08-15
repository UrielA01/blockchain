import hashlib


def calculate_hash(data: str) -> str:
    return hashlib.sha256(data).hexdigest()
