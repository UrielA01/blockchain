from flask import Flask, request, jsonify
import sys
import json
import atexit

from src.core.blocks.block import Block
from src.core.blocks.block_validation import BlockValidation, BlockValidationException
from src.core.transactions.transaction import Transaction
from src.core.transactions.transaction_validation import TransactionException, TransactionValidation
from src.network.node import SendNode
from src.utils.crypto_utils import calculate_sha256
from src.utils.io_known_nodes import remove_known_node, add_known_nodes
from src.utils.io_mem_pool import store_transactions_in_memory
from src.wallet.initialize_blockchain import initialize_blockchain
from src.wallet.wallet import Wallet
from src.network.node import Node
from src.network.network import Network
app = Flask(__name__)
app.json.sort_keys = False

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

host, port = get_host_port()
my_node = Node(host, port)
my_wallet = Wallet()
add_known_nodes([my_node.to_dict])
network = Network(my_node)
blockchain = initialize_blockchain(my_wallet=my_wallet, network=network)

send_node = SendNode(wallet=my_wallet, network=network)


def cleanup():
    remove_known_node(my_node.to_dict)
    print("Closing server, removing self from known_nodes")

atexit.register(cleanup)

def generate_message_id(message):
    return calculate_sha256(json.dumps(message, sort_keys=True).encode())

processed_messages = set()

@app.route("/transaction", methods=['POST'])
def validate_transaction():
    content = request.json
    try:
        if content.get('transaction'):
            transaction = Transaction.from_json(content.get('transaction'))
            validate = TransactionValidation(transaction=transaction, blockchain=blockchain)
            validate.validate()
            store_transactions_in_memory([transaction.to_dict])
    except TransactionException as transaction_exception:
        return f'{transaction_exception}', 400
    return "Transaction success", 200

@app.route("/block", methods=['POST'])
def receive_block():
    content = request.json
    message_id = generate_message_id(content)

    if message_id in processed_messages:
        print(f'Message already processed - {message_id}')
        return 'Message already processed', 200

    processed_messages.add(message_id)

    print(f"Processing message: {message_id}")
    try:
        if content.get('block'):
            new_block = Block.from_json(content.get('block'))
            validate = BlockValidation(block=new_block, blockchain=blockchain)
            validate.validate()
            blockchain.add_new_block(new_block=new_block)
            send_node.broadcast_block(new_block)
    except BlockValidationException as e:
        return f'{e}', 400
    return "New block added", 200

@app.route("/chain", methods=['GET'])
def send_chain():
    data = []
    current_block = blockchain.last_block
    while current_block:
        data.append(current_block.to_dict)
        current_block = current_block.previous_block
    return jsonify(data)

@app.route("/advertise", methods=['POST'])
def advertise():
    content = request.json
    node = content["node"]
    try:
        new_node = Node.from_json(node)
        network.add_known_nodes([new_node])
    except Exception as e:
        return f'{e}', 400
    return "New node advertisement success", 200


@app.route("/known_nodes", methods=['GET'])
def known_node():
    known_nodes_dict = [node.to_dict for node in network.known_nodes]
    return jsonify(known_nodes_dict)

@app.route("/mine", methods=['POST'])
def mine():
    new_block = blockchain.create_new_block()
    message_id = generate_message_id({"block": new_block.to_dict})
    processed_messages.add(message_id)
    send_node.broadcast_block(new_block)
    return "Mined successfully", 200

if __name__ == '__main__':
    app.run(host=host, port=port)
