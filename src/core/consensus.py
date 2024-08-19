from src.core.block import Block

class Consensus:
    def __init__(self):
        self.difficulty = 4

    def valid_nonce(self, block: Block, nonce: int) -> bool:
        block.nonce = nonce
        return block.hash[:self.difficulty] == "0" * self.difficulty

    def proof_of_work(self, block: Block) -> int:
        nonce = 0
        while not self.valid_nonce(block, nonce):
            nonce += 1
        return nonce

    def valid_new_block(self, last_block: Block, new_block: Block) -> bool:
        if not new_block.index == last_block.index + 1:
            return False

        if not new_block.previous_hash == last_block.hash:
            return False

        if not self.valid_nonce(new_block, new_block.nonce):
            return False

        return True

    def valid_chain(self, last_block: Block) -> bool:
        while last_block.index > 1 and last_block.previous_block:
            if not self.valid_new_block(last_block.previous_block, last_block):
                return False
            last_block = last_block.previous_block
