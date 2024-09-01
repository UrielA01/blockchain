import copy

from src.core.blocks.block import BlockHeader, Block
from src.core.transactions.transaction import Transaction, TransactionOutput
from src.core.transactions.transaction_validation import TransactionValidation, TransactionException
from src.utils.consts import NUMBER_OF_LEADING_ZEROS_IN_HASH, MINER_REWARD
from src.wallet.wallet import Wallet


class BlockException(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)
        self.message = message

    def __str__(self):
        return self.message

class ProofOfWork:
    def __init__(self):
        pass

    @staticmethod
    def is_valid_nonce(block_header: BlockHeader):
        block_header_hash = block_header.hash
        desired_starting_zeros = "".join([str(0) for _ in range(NUMBER_OF_LEADING_ZEROS_IN_HASH)])
        return block_header_hash.startswith(desired_starting_zeros)

    @staticmethod
    def find_nonce(block_header: BlockHeader):
        header_copy = copy.deepcopy(block_header)
        nonce = header_copy.nonce
        while not ProofOfWork.is_valid_nonce(header_copy):
            nonce += 1
            header_copy.nonce = nonce
        return nonce

    @staticmethod
    def get_coin_base_transaction(transaction_fees: float, miner_wallet: Wallet) -> Transaction:
        transaction_output = TransactionOutput(amount=transaction_fees + MINER_REWARD, public_key_hash=miner_wallet.public_key_hash)
        return Transaction(inputs=[], outputs=[transaction_output], is_coin_base=True)


from src.core.blockchain import Blockchain
class BlockValidation:
    def __init__(self, blockchain: Blockchain, block: Block):
        self.blockchain = blockchain
        self.block = block

    def validate_prev_block(self):
        if not (self.blockchain.last_block.header.hash == self.block.header.previous_hash):
            raise BlockException("Invalid previous hash")

    def validate_hash(self):
        if not ProofOfWork.is_valid_nonce(self.block.header):
            raise BlockException("Invalid hash")

    def validate_transactions(self):
        try:
            for tx in self.block.transactions:
                validate = TransactionValidation(transaction=tx, blockchain=self.blockchain)
                validate.validate()
        except TransactionException:
            raise BlockException("Invalid transactions")

    def validate(self):
        if self.blockchain.last_block:
            self.validate_prev_block()
        self.validate_hash()
        self.validate_transactions()

