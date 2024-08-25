from src.core.block import BlockHeader, Block
from src.core.blockchain import Blockchain
from src.core.transactions.transaction_validation import TransactionValidation, TransactionException
from src.utils.consts import NUMBER_OF_LEADING_ZEROS_IN_HASH

class BlockValidationException(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

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
        nonce = block_header.nonce
        while not ProofOfWork.is_valid_nonce(block_header):
            nonce += 1
        return nonce

class BlockValidation:
    def __init__(self, blockchain: Blockchain, new_block: Block):
        self.blockchain = blockchain
        self.new_block = new_block

    def is_valid_prev_block(self):
        if not self.blockchain.last_block.header.hash == self.new_block.header.previous_hash:
            raise BlockValidationException("", "Invalid previous hash")

    def is_valid_hash(self):
        if not ProofOfWork.is_valid_nonce(self.new_block.header):
            raise BlockValidationException("", "Invalid hash")

    def is_valid_transactions(self):
        try:
            for tx in self.new_block.transactions:
                validate = TransactionValidation(transaction=tx, blockchain=self.blockchain)
                validate.validate_scripts()
                validate.validate_funds()
        except TransactionException:
            raise BlockValidationException("", "Invalid transactions")

