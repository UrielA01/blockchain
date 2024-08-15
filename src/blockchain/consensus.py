from typing import List
from block import Block


class Consensus:
    def __init__(self):
        self.difficulty = 4

    def valid_nonce(self, block: Block, nonce: int) -> bool:
        block.nonce = nonce
        return block.compute_hash()[:self.difficulty] == "0" * self.difficulty

    def proof_of_work(self, block: Block) -> int:
        nonce = 0
        while not self.valid_nonce(block, nonce):
            nonce += 1
        return nonce

    def valid_chain(self, chain: List[Block]) -> bool:
        # Determine if a given blockchain is valid
        previous_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            current_block = chain[current_index]

            # Check that the hash of the block is correct
            if current_block.previous_hash != previous_block.compute_hash():
                return False

            # Check that the Proof of Work is correct
            if not self.valid_nonce(current_block, current_block.nonce):
                return False

            previous_block = current_block
            current_index += 1

        return True
