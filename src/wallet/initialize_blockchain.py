from src.core.blockchain import Blockchain
from src.core.blocks.block_validation import BlockValidationException
from src.core.transactions.transaction import TransactionInput, TransactionOutput, Transaction
from src.core.transactions.transaction_validation import TransactionValidation, TransactionException
from src.network.network import Network
from src.utils.io_mem_pool import store_transactions_in_memory
from src.wallet.wallet import Wallet
from src.users.albert import private_key as albert_private_key
from src.users.bertrand import private_key as bertrand_private_key
from src.users.camille import private_key as camille_private_key


albert_wallet = Wallet(private_key=albert_private_key)
bertrand_wallet = Wallet(private_key=bertrand_private_key)
camille_wallet = Wallet(private_key=camille_private_key)


def initialize_blockchain(my_wallet: Wallet, network: Network) -> Blockchain:
    network.join_network()
    blockchain_dict = network.get_longest_blockchain()
    blockchain = None

    if blockchain_dict:
        blockchain = Blockchain.from_json_list(blockchain_dict, wallet=my_wallet)
    if not blockchain:
        blockchain = Blockchain(wallet=my_wallet)

        blockchain.create_new_block(transactions=[])

        input_0 = TransactionInput(transaction_hash=blockchain.last_block.transactions[0].hash,
                                   output_index=0)
        output_0 = TransactionOutput(public_key_hash=my_wallet.public_key_hash,
                                     amount=3)
        output_1 = TransactionOutput(public_key_hash=albert_wallet.public_key_hash,
                                     amount=3)
        transaction = Transaction(outputs=[output_0, output_1], inputs=[input_0])
        transaction.sign_inputs(my_wallet)

        try:
            validate = TransactionValidation(blockchain, transaction)
            validate.validate()
            store_transactions_in_memory([transaction.to_dict])
            blockchain.create_new_block()
        except (TransactionException, BlockValidationException) as e:
            print(e)
            raise TransactionException("", "Invalid transaction")

        # Uncomment to test transactions from mempool
        # input_0 = TransactionInput(transaction_hash=blockchain.last_block.transactions[0].hash,
        #                            output_index=0)
        # output_0 = TransactionOutput(public_key_hash=my_wallet.public_key_hash,
        #                              amount=1)
        # output_1 = TransactionOutput(public_key_hash=camille_wallet.public_key_hash,
        #                              amount=1.5)
        # transaction = Transaction(outputs=[output_0, output_1], inputs=[input_0])
        # transaction.sign_inputs(my_wallet)
        # store_transactions_in_memory([transaction.to_dict])

    return blockchain
