import copy
import math
from typing import List

from src.utils.crypto_utils import calculate_sha256


class Node:
    def __init__(self, value: str, left_child=None, right_child=None):
        self.value = value
        self.left_child = left_child
        self.right_child = right_child


class MerkleTree:
    def __init__(self, transactions_data: List[bytes]):
        self.root = self.build_merkle_tree(transactions_data)

    @staticmethod
    def compute_tree_depth(number_of_leaves: int) -> int:
        return math.ceil(math.log2(number_of_leaves))

    @staticmethod
    def is_power_of_2(number_of_leaves: int) -> bool:
        return math.log2(number_of_leaves).is_integer()

    def fill_set(self, leaves: List[Node]) -> List[Node]:
        """
        Fills the given list of nodes to make it a complete binary tree.

        Args:
            leaves (list[str]): The list of nodes to be filled.

        Returns:
            list[str]: The filled list of nodes.

        """
        num_of_leaves = len(leaves)
        if num_of_leaves % 2 == 1:
            leaves.append(copy.deepcopy(leaves[-1]))
        if self.is_power_of_2(num_of_leaves):
            return leaves
        total_number_of_leaves = 2 ** self.compute_tree_depth(
            num_of_leaves)
        is_even_number_of_leaves = num_of_leaves % 2 == 0
        if is_even_number_of_leaves:
            for i in range(num_of_leaves, total_number_of_leaves, 2):
                leaves = leaves + \
                         [leaves[-2], leaves[-1]]
        else:
            for i in range(num_of_leaves, total_number_of_leaves):
                leaves.append(leaves[-1])
        return leaves

    def build_merkle_tree(self, transactions_data: List[bytes]) -> Node:
        leaves = [Node(value=calculate_sha256(data))
                            for data in transactions_data]
        leaves = self.fill_set(leaves)
        tree_depth = self.compute_tree_depth(len(leaves))

        new_nodes = []
        for i in range(0, tree_depth):
            num_nodes = 2**(tree_depth - i)
            new_nodes = []
            for j in range(0, num_nodes, 2):
                child_node_0 = leaves[j]
                child_node_1 = leaves[j + 1]
                new_node = Node(value=calculate_sha256(
                    f'{child_node_0.value}{child_node_1.value}'),
                    left_child=child_node_0,
                    right_child=child_node_1)
                new_nodes.append(new_node)
            leaves = new_nodes
        root = new_nodes[0]
        return root
