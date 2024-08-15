import binascii
from Crypto.Hash import RIPEMD160, SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
import base58


from utils.crypto_utils import calculate_ripemd160, calculate_sha256


class Wallet:
    def __init__(self):
        self.private_key, self.public_key = initialize_wallet()
        self.address = base58.b58encode(
            hash_address(self.public_key))

    def sign(self, transaction: bytes) -> bytes:
        """
        Sign a message with the wallet's private key.

        :param message: The message to sign (in bytes).
        :return: The digital signature (base64 encoded).
        """
        # Create a SHA-256 hash of the message
        hash_obj = SHA256.new(transaction)

        # Sign the hash using the private key
        signature = pkcs1_15.new(self.private_key).sign(hash_obj)

        return signature

    @staticmethod
    def convert_signature_to_str(signature: bytes) -> str:
        return binascii.hexlify(signature).decode("utf-8")

    def verify_signature(self, message: bytes, signature: bytes) -> bool:
        """
        Verify a digital signature using the wallet's public key.

        :param message: The original message (in bytes).
        :param signature: The signature to verify (in bytes).
        :return: True if the signature is valid, False otherwise.
        """
        # Create a SHA-256 hash of the message
        hash_obj = SHA256.new(message)

        try:
            # Verify the signature
            pkcs1_15.new(RSA.import_key(self.public_key)
                         ).verify(hash_obj, signature)
            return True
        except (ValueError, TypeError):
            return False


def initialize_wallet():
    private_key = RSA.generate(2048)
    public_key = private_key.publickey().export_key()
    return private_key, public_key


def hash_address(key: bytes) -> str:
    first_hash = calculate_sha256(key)
    first_hash = bytearray(first_hash, "utf-8")
    return calculate_ripemd160(first_hash)
