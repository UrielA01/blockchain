import time

from src.core.block import Block
from src.core.blockchain import Blockchain
from src.core.transaction import TransactionInput, TransactionOutput
from src.wallet.wallet import Wallet
from src.users.albert import private_key as albert_private_key
from src.users.bertrand import private_key as bertrand_private_key
from src.users.camille import private_key as camille_private_key


albert_wallet = Wallet(private_key=albert_private_key)
bertrand_wallet = Wallet(private_key=bertrand_private_key)
camille_wallet = Wallet(private_key=camille_private_key)


def initialize_blockchain():
    blockchain = Blockchain()

    timestamp_0 = time.time()
    input_0 = TransactionInput(transaction_hash="abcd1234",
                               output_index=0)
    output_0 = TransactionOutput(public_key_hash=albert_wallet.public_key_hash,
                                 amount=40)
    inputs = [input_0.to_json()]
    outputs = [output_0.to_json()]
    block_0 = Block(
        transaction_data={"inputs": inputs, "outputs": outputs},
        timestamp=timestamp_0
    )

    timestamp_1 = time.time()
    input_0 = TransactionInput(transaction_hash=block_0.transaction_hash,
                               output_index=0)
    output_0 = TransactionOutput(public_key_hash=bertrand_wallet.public_key_hash,
                                 amount=30)
    output_1 = TransactionOutput(public_key_hash=albert_wallet.public_key_hash,
                                 amount=10)
    inputs = [input_0.to_json()]
    outputs = [output_0.to_json(), output_1.to_json()]

    block_1 = Block(
        transaction_data={"inputs": inputs, "outputs": outputs},
        timestamp=timestamp_1,
        previous_block=block_0
    )

    timestamp_2 = time.time()
    input_0 = TransactionInput(transaction_hash=block_1.transaction_hash,
                               output_index=1)
    output_0 = TransactionOutput(public_key_hash=camille_wallet.public_key_hash,
                                 amount=10)
    inputs = [input_0.to_json()]
    outputs = [output_0.to_json()]
    block_2 = Block(
        transaction_data={"inputs": inputs, "outputs": outputs},
        timestamp=timestamp_2,
        previous_block=block_1
    )

    timestamp_3 = time.time()
    input_0 = TransactionInput(transaction_hash=block_1.transaction_hash,
                               output_index=0)
    output_0 = TransactionOutput(public_key_hash=camille_wallet.public_key_hash,
                                 amount=5)
    output_1 = TransactionOutput(public_key_hash=bertrand_wallet.public_key_hash,
                                 amount=25)
    inputs = [input_0.to_json()]
    outputs = [output_0.to_json(), output_1.to_json()]
    block_3 = Block(
        transaction_data={"inputs": inputs, "outputs": outputs},
        timestamp=timestamp_3,
        previous_block=block_2
    )
    return block_3
