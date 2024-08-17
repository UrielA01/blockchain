import binascii
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
import base58


from utils.crypto_utils import calculate_ripemd160, calculate_sha256


class Wallet:
    def __init__(self):
        self.private_key, self.public_key, self.address = initialize_wallet()

    def sign(self, transaction: bytes) -> bytes:
        """
        Sign a message with the wallet's private key.

        :param message: The message to sign (in bytes).
        :return: The digital signature (base64 encoded).
        """
        # Create a SHA-256 hash of the message
        hash_obj = calculate_sha256(transaction)

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
        :return: True if the signature is valid, False otherwise.
        """
        # Create a SHA-256 hash of the message
        hash_obj = calculate_sha256(message)

        try:
            # Verify the signature
            pkcs1_15.new(RSA.import_key(public_key)
                         ).verify(hash_obj, signature)
            return True
        except (ValueError, TypeError):
            return False


def initialize_wallet():
    private_key = RSA.generate(2048)
    public_key = private_key.publickey().export_key()

    first_key_hash = calculate_sha256(public_key)
    second_key_hash = calculate_ripemd160(first_key_hash)
    address = base58.b58encode(second_key_hash)
    return private_key, public_key, address
