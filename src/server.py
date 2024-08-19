import sys
import timeit
from dataclasses import asdict
from uuid import uuid4

from flask import Flask, jsonify, request

from src.core.block import Block
from src.core.transaction import Transaction
from src.network.node import NodeTransaction
from src.wallet.initialize_blockchain import initialize_blockchain

app = Flask(__name__)
app.json.sort_keys = False


node_identifier = str(uuid4()).replace("-", "")

blockchain = initialize_blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    start = timeit.default_timer()

    reward_transaction = Transaction(
        sender="0",
        recipient=node_identifier,
        amount=1
    )
    blockchain.new_transaction(
        reward_transaction
    )

    block = blockchain.add_block()
    stop = timeit.default_timer()

    response = {
        "message": "New Block Forged",
        **(asdict(block)),
        "time": stop - start
    }

    return jsonify(response), 200


@app.route("/transactions", methods=['POST'])
def validate_transaction():
    content = request.json
    try:
        node = NodeTransaction(blockchain)
        node.receive(transaction=content["transaction"])
        node.validate_transaction()
        node.validate_funds()
        node.broadcast()
    except Exception as transaction_exception:
        return f'{transaction_exception}', 400
    return "Transaction success", 200


@app.route("/transactions/new", methods=['POST'])
def new_transaction():
    values = request.get_json()

    transaction = Transaction(
        values["sender"], values["recipient"], values["amount"])

    # if not transaction.valid_transaction():
    #     return "Missing values", 400

    index = blockchain.new_transaction(transaction)
    blockchain.broadcast_transaction(transaction)
    response = {"message": f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route("/transactions/receive", methods=['POST'])
def receive_transaction():
    values = request.get_json()

    transaction = Transaction(
        values["sender"], values["recipient"], values["amount"])

    # if not transaction.valid_transaction():
    #     return "Missing values", 400

    index = blockchain.new_transaction(transaction)
    response = {"message": f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route("/chain", methods=['GET'])
# Deprecated for now
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        "message": "New nodes have been added",
        "total_nodes": list(blockchain.nodes)
    }
    return jsonify(response), 201


@app.route('/block/new', methods=['POST'])
def receive_block():
    block_as_json = request.get_json()

    block = Block(
        index=block_as_json["index"],
        timestamp=block_as_json["timestamp"],
        transactions=block_as_json["transactions"],
        nonce=block_as_json["nonce"],
        previous_hash=block_as_json["previous_hash"]
    )

    added = blockchain.receive_block(block)

    if not added:
        response = {
            "message": "New block is invalid, not added",
            "block": block_as_json
        }
        return jsonify(response), 401

    response = {
        "message": "New block have been added",
        "block": block_as_json
    }
    return jsonify(response), 201


@app.route("/nodes/resolve", methods=["GET"])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            "message": "Our chain was replaced",
            "new_chain": blockchain.chain
        }
    else:
        response = {
            "message": "Our chain is authoritative",
            "chain": blockchain.chain
        }

    return jsonify(response), 200


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(host="0.0.0.0", port=port)
