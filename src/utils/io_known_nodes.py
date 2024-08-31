import json
import os
from typing import List

known_nodes = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../mem_pools/network_nodes.json'))

def get_known_nodes() -> List[dict]:
    with open(known_nodes, "r") as file_obj:
        known_nodes_str = file_obj.read()
        known_nodes_dict = json.loads(known_nodes_str)
    return known_nodes_dict

def add_known_nodes(nodes: List[dict]):
    current_known_nodes = get_known_nodes()
    for node in nodes:
        if node not in current_known_nodes:
            current_known_nodes.append(node)
    text = json.dumps(current_known_nodes, indent=4)
    with open(known_nodes, "w") as file_obj:
        file_obj.write(text)

def remove_known_node(node: dict):
    current_known_nodes = get_known_nodes()
    current_known_nodes.remove(node)
    text = json.dumps(current_known_nodes, indent=4)
    with open(known_nodes, "w") as file_obj:
        file_obj.write(text)