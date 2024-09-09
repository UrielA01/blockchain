import sys
import json
import os
import socket
import argparse

from src.utils.crypto_utils import calculate_sha256
from src.utils.io_known_nodes import remove_known_node
from src.network.node import Node

def get_host_port():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Port")
    parser.add_argument( "--hostname", help="Hostname")
    args = parser.parse_args()

    hostname = args.hostname if args.hostname else os.getenv('HOSTNAME', socket.gethostname())
    port_num = args.port if args.port else os.getenv('PORT', 5000)
    return hostname, port_num

def cleanup(my_node: Node):
    remove_known_node(my_node.to_dict)
    print("Closing server, removing self from known_nodes")

def generate_message_id(message):
    return calculate_sha256(json.dumps(message, sort_keys=True).encode())