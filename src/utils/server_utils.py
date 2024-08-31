import sys
import json

from src.utils.crypto_utils import calculate_sha256
from src.utils.io_known_nodes import remove_known_node
from src.network.node import Node


def get_host_port(default_host='127.0.0.1', default_port=5000):
    port_num = default_port
    hostname = default_host
    try:
        if len(sys.argv) >= 2:
            port_num = int(sys.argv[1])
        if len(sys.argv) >= 3:
            hostname = sys.argv[2]
    except ValueError:
        port_num = default_port
    return hostname, port_num

def cleanup(my_node: Node):
    remove_known_node(my_node.to_dict)
    print("Closing server, removing self from known_nodes")

def generate_message_id(message):
    return calculate_sha256(json.dumps(message, sort_keys=True).encode())