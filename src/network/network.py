from src.network.node import Node
from src.utils.io_known_nodes import add_known_nodes, get_known_nodes
from typing import List


class Network:

    def __init__(self, node: Node):
        self.node = node

    @property
    def known_nodes(self) -> List[Node]:
        known_nodes = []
        for node in get_known_nodes():
            node = Node.from_json(node)
            if not (node == self.node):
                known_nodes.append(node)
        return known_nodes

    def add_known_nodes(self, nodes: List[Node]):
        for node in nodes:
            if node not in self.known_nodes:
                self.known_nodes.append(node)
                add_known_nodes([node.to_dict for node in nodes])

    @property
    def other_nodes_exist(self) -> bool:
        if len(self.known_nodes) == 0:
            return False
        elif len(self.known_nodes) == 1 and self.known_nodes[0].hostname == self.node.hostname:
            return False
        else:
            return True

    def advertise_to_all_known_nodes(self):
        for node in self.known_nodes:
            if node.hostname != self.node.hostname:
                node.advertise(self.node.to_dict)

    def set_known_nodes_from_known_nodes(self):
        for known_node in self.known_nodes:
            if known_node != self.node:
                known_nodes_of_known_node = known_node.get_known_nodes()
                if known_nodes_of_known_node:
                    self.add_known_nodes([Node.from_json(node) for node in known_nodes_of_known_node])

    def join_network(self):
        if self.other_nodes_exist:
            self.advertise_to_all_known_nodes()
            self.set_known_nodes_from_known_nodes()
            self.advertise_to_all_known_nodes()


    def get_longest_blockchain(self):
        longest_blockchain_size = 0
        longest_blockchain = None
        for node in self.known_nodes:
            if node.hostname != self.node.hostname:
                blockchain = node.get_blockchain()
                blockchain_length = len(blockchain)
                if blockchain_length > longest_blockchain_size:
                    longest_blockchain_size = blockchain_length
                    longest_blockchain = blockchain
        return longest_blockchain