from flask import Flask, request, jsonify
import signal
import sys

from src.core.blocks.block import Block
from src.core.blocks.block_validation import BlockValidation, BlockException
from src.core.transactions.transaction import Transaction
from src.core.transactions.transaction_validation import TransactionValidationException, TransactionValidation
from src.network.node import Node
from src.utils.io_known_nodes import add_known_nodes
from src.utils.io_mem_pool import store_transactions_in_memory
from src.utils.server_utils import get_host_port, cleanup, generate_message_id
from src.wallet.initialize_blockchain import initialize_blockchain
from src.wallet.wallet import Wallet
from src.network.network import Network
app = Flask(__name__)
app.json.sort_keys = False

host, port = get_host_port()
my_node = Node(host, port)
my_wallet = Wallet()
add_known_nodes([my_node.to_dict])
network = Network(my_node, my_wallet)
blockchain = initialize_blockchain(my_wallet=my_wallet, network=network)

processed_messages = set()

def handle_close(*args):
    cleanup(my_node)
    sys.exit(0)
signal.signal(signal.SIGINT, handle_close)
signal.signal(signal.SIGTERM, handle_close)
@app.route("/", methods=['GET'])
def index_route():
    return "Hello world", 200

@app.route("/transaction", methods=['POST'])
def validate_transaction():
    content = request.json
    try:
        if content.get('transaction'):
            transaction = Transaction.from_json(content.get('transaction'))
            validate = TransactionValidation(transaction=transaction, blockchain=blockchain)
            validate.validate()
            store_transactions_in_memory([transaction.to_dict])
    except TransactionValidationException as transaction_exception:
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
            network.broadcast_block(new_block)
    except BlockException as e:
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
    new_node = Node.from_json(node)
    network.add_known_nodes([new_node])
    return jsonify({"status": "ok"})


@app.route("/known_nodes", methods=['GET'])
def known_node():
    known_nodes_dict = [node.to_dict for node in network.known_nodes]
    return jsonify(known_nodes_dict)

@app.route("/mine", methods=['POST'])
def mine():
    new_block = blockchain.create_new_block()
    message_id = generate_message_id({"block": new_block.to_dict})
    processed_messages.add(message_id)
    network.broadcast_block(new_block)
    return "Mined successfully", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)
