import binascii

import base58
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from src.utils.crypto_utils import calculate_sha256, calculate_ripemd160


class Wallet:
    def __init__(self, private_key: str = None):
        if private_key:
            self.private_key = RSA.import_key(private_key)
        else:
            self.private_key = RSA.generate(2048)
        self.public_key = self.private_key.publickey().export_key()

        first_key_hash = calculate_sha256(self.public_key)
        self.public_key_hash = calculate_ripemd160(first_key_hash)
        self.address = base58.b58encode(self.public_key_hash)

    def sign(self, transaction: bytes) -> bytes:
        """
        Sign a message with the wallet's private key.

        :param transaction: The message to sign (in bytes).
        :return: The digital signature (base64 encoded).
        """
        # Create an SHA-256 hash of the message
        hash_obj = SHA256.new(transaction)

        # Sign the hash using the private key
        signature = pkcs1_15.new(self.private_key).sign(hash_obj)

        return signature

    @staticmethod
    def convert_signature_to_str(signature: bytes) -> str:
        return binascii.hexlify(signature).decode("utf-8")

    @staticmethod
    def valid_signature(signature: bytes, public_key: bytes, message: bytes) -> bool:
        """
        Verify a digital signature using public key.

        :param message: The original message (in bytes).
        :param signature: The signature to verify (in bytes).
        :param public_key: public key (in bytes).
        :return: True if the signature is valid, False otherwise.
        """
        # Create an SHA-256 hash of the message
        hash_obj = SHA256.new(message)

        try:
            # Verify the signature
            pkcs1_15.new(RSA.import_key(public_key)
                         ).verify(hash_obj, signature)
            return True
        except (ValueError, TypeError):
            return False
