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

@app.route("/transactions", methods=['POST'])
def validate_transaction():
    content = request.json
    try:
        node = NodeTransaction(blockchain)
        node.receive(transaction=content)
        node.validate_transaction()
        node.validate_funds()
        node.broadcast()
    except Exception as transaction_exception:
        return f'{transaction_exception}', 400
    return "Transaction success", 200

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(host="0.0.0.0", port=port)
