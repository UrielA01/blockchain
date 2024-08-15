import math
from typing import List
from utils.crypto_utils import calculate_sha256


class Node:
    def __init__(self, value: int, left_child=None, right_child=None):
        self.value = value
        self.left_child = left_child
        self.right_child = right_child


class MerkleTree:
    def __init__(self):
        self.root = None

    def compute_tree_depth(self, number_of_leaves: int) -> int:
        return math.ceil(math.log2(number_of_leaves))

    def is_power_of_2(number_of_leaves: int) -> bool:
        return math.log2(number_of_leaves).is_integer()

    def fill_set(self, list_of_nodes: list[str]) -> list[str]:
        """
        Fills the given list of nodes to make it a complete binary tree.

        Args:
            list_of_nodes (list[str]): The list of nodes to be filled.

        Returns:
            list[str]: The filled list of nodes.

        """
        current_number_of_leaves = len(list_of_nodes)
        if self.is_power_of_2(current_number_of_leaves):
            return list_of_nodes
        total_number_of_leaves = 2 ** self.compute_tree_depth(
            current_number_of_leaves)
        is_even_number_of_leaves = current_number_of_leaves % 2 == 0
        if is_even_number_of_leaves:
            for i in range(current_number_of_leaves, total_number_of_leaves, 2):
                list_of_nodes = list_of_nodes + \
                    [list_of_nodes[-2], list_of_nodes[-1]]
        else:
            for i in range(current_number_of_leaves, total_number_of_leaves):
                list_of_nodes.append(list_of_nodes[-1])
        return list_of_nodes

    def build_merkle_tree(self, node_data: List[str]) -> Node:
        old_set_of_nodes = [Node(calculate_sha256(data))
                            for data in node_data]
        old_set_of_nodes = self.fill_set(old_set_of_nodes)
        tree_depth = self.compute_tree_depth(len(old_set_of_nodes))

        for i in range(0, tree_depth):
            num_nodes = 2**(tree_depth - i)
            new_set_of_nodes = []
            for j in range(0, num_nodes, 2):
                child_node_0 = old_set_of_nodes[j]
                child_node_1 = old_set_of_nodes[j + 1]
                new_node = Node(value=calculate_sha256(
                    f'{child_node_0.value}{child_node_1.value}'),
                    left_child=child_node_0,
                    right_child=child_node_1)
                new_set_of_nodes.append(new_node)
            old_set_of_nodes = new_set_of_nodes
        return new_set_of_nodes[0]
