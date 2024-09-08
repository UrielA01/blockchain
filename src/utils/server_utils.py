import sys
import json
import os
import socket

from src.utils.crypto_utils import calculate_sha256
from src.utils.io_known_nodes import remove_known_node
from src.network.node import Node

def get_host_port():
    default_host = socket.gethostname()
    default_port = 5000
    try:
        port_num = int(sys.argv[1])
    except (ValueError, IndexError):
        port_num = os.getenv('PORT', default_port)
    try:
        hostname = sys.argv[2]
    except (ValueError, IndexError):
        hostname = os.getenv('HOST', default_host)
    return hostname, port_num

def cleanup(my_node: Node):
    remove_known_node(my_node.to_dict)
    print("Closing server, removing self from known_nodes")

def generate_message_id(message):
    return calculate_sha256(json.dumps(message, sort_keys=True).encode())