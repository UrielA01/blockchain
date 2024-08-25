from src.core.blockchain import Blockchain
from src.core.transactions.transaction import TransactionInput, TransactionOutput, Transaction
from src.wallet.wallet import Wallet
from src.users.albert import private_key as albert_private_key
from src.users.bertrand import private_key as bertrand_private_key
from src.users.camille import private_key as camille_private_key


albert_wallet = Wallet(private_key=albert_private_key)
bertrand_wallet = Wallet(private_key=bertrand_private_key)
camille_wallet = Wallet(private_key=camille_private_key)


def initialize_blockchain() -> Blockchain:
    blockchain = Blockchain()

    input_0 = TransactionInput(transaction_hash="abcd1234",
                               output_index=0)
    output_0 = TransactionOutput(public_key_hash=albert_wallet.public_key_hash,
                                 amount=40)
    transaction = Transaction(outputs=[output_0], inputs=[input_0])
    block_0 = blockchain.add_new_block(transaction)

    input_0 = TransactionInput(transaction_hash=block_0.transactions[0].hash,
                               output_index=0)
    output_0 = TransactionOutput(public_key_hash=bertrand_wallet.public_key_hash,
                                 amount=30)
    output_1 = TransactionOutput(public_key_hash=albert_wallet.public_key_hash,
                                 amount=10)
    transaction = Transaction(outputs=[output_0, output_1], inputs=[input_0])
    transaction.sign_inputs(camille_wallet)

    block_1 = blockchain.add_new_block(transaction)

    input_0 = TransactionInput(transaction_hash=block_1.transactions[0].hash,
                               output_index=1)
    output_0 = TransactionOutput(public_key_hash=camille_wallet.public_key_hash,
                                 amount=10)
    transaction = Transaction(outputs=[output_0], inputs=[input_0])
    transaction.sign_inputs(albert_wallet)

    block_2 = blockchain.add_new_block(transaction)

    input_0 = TransactionInput(transaction_hash=block_2.transactions[0].hash,
                               output_index=0)
    output_0 = TransactionOutput(public_key_hash=camille_wallet.public_key_hash,
                                 amount=5)
    output_1 = TransactionOutput(public_key_hash=bertrand_wallet.public_key_hash,
                                 amount=25)
    transaction = Transaction(outputs=[output_0, output_1], inputs=[input_0])
    transaction.sign_inputs(albert_wallet)

    print(transaction.send_to_nodes())

    blockchain.add_new_block(transaction)

    return blockchain
