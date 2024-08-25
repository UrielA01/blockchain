from src.core.block import BlockHeader
from src.core.blockchain import Blockchain
from src.utils.consts import NUMBER_OF_LEADING_ZEROS_IN_HASH


class NewBlock:
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain
        self.new_block = None

    @staticmethod
    def is_valid_nonce(block_header: BlockHeader):
        block_header_hash = block_header.hash
        desired_starting_zeros = "".join([str(0) for _ in range(NUMBER_OF_LEADING_ZEROS_IN_HASH)])
        return block_header_hash.startswith(desired_starting_zeros)

    @staticmethod
    def set_nonce(block_header: BlockHeader):
        nonce = block_header.nonce
        while not NewBlock.is_valid_nonce(block_header):
            nonce += 1
        block_header.nonce = nonce
        return nonce