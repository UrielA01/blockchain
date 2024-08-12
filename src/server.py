from dataclasses import asdict
from uuid import uuid4
from flask import Flask, jsonify, request
from blockchain import Block, Blockchain
import sys

# Instantiate our node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace("-", "")

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.last_block.hash
    block = blockchain.add_block(previous_hash)

    response = {
        "message": "New Block Forged",
        **(asdict(block))
    }

    return jsonify(response), 200


@app.route("/transactions/new", methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ["sender", "sender", "amount"]
    if not all(k in values for k in required):
        return "Missing values", 400

    # Create a new Transaction
    index = blockchain.new_transaction(
        values["sender"], values["recipient"], values["amount"])
    response = {"message": f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route("/chain", methods=['GET'])
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
def recive_block():
    block_as_json = request.get_json()

    block = Block(
        index=block_as_json["index"],
        timestamp=block_as_json["timestamp"],
        transactions=block_as_json["transactions"],
        nonce=block_as_json["nonce"],
        previous_hash=block_as_json["previous_hash"]
    )

    blockchain.recive_block(block)

    response = {
        "message": "New block have been added",
        "block": block_as_json
    }
    return jsonify(response), 201


@app.route("/nodes/resolve", methods=["GET"])
def consensus():
    repalced = blockchain.resolve_conflicts()

    if repalced:
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
