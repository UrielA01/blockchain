from Crypto.Hash import RIPEMD160, SHA256


def calculate_sha256(data: str | bytes) -> str:
    if type(data) == str:
        data = bytearray(data, "utf-8")
    hash = SHA256.new(data)
    return hash.hexdigest()


def calculate_ripemd160(data: str | bytes) -> str:
    if type(data) == str:
        data = bytearray(data, "utf-8")
    hash = RIPEMD160.new(data)
    return hash.hexdigest()
