from uuid import uuid4

from flask import Flask, request

from src.core.blocks.block import Block
from src.core.blocks.block_validation import BlockValidation, BlockValidationException
from src.core.transactions.transaction import Transaction
from src.core.transactions.transaction_validation import TransactionException, TransactionValidation
from src.network.node import SendNode
from src.wallet.initialize_blockchain import initialize_blockchain
from src.wallet.wallet import Wallet

app = Flask(__name__)
app.json.sort_keys = False

node_identifier = str(uuid4()).replace("-", "")

blockchain = initialize_blockchain()

my_wallet = Wallet()
send_node = SendNode(wallet=my_wallet)

@app.route("/transaction", methods=['POST'])
def validate_transaction():
    content = request.json
    try:
        transaction = Transaction.from_json(content.get('transaction'))
        validate = TransactionValidation(transaction=transaction, blockchain=blockchain)
        validate.validate_scripts()
        validate.validate_funds()
        transaction.store()
        send_node.broadcast_transaction(transaction)
    except TransactionException as transaction_exception:
        return f'{transaction_exception}', 400
    return "Transaction success", 200

@app.route("/block", methods=['POST'])
def validate_block():
    content = request.json
    try:
        new_block = Block.from_json(content.get('block'))
        validate = BlockValidation(new_block=new_block, blockchain=blockchain)
        validate.is_valid_prev_block()
        validate.is_valid_hash()
        validate.is_valid_transactions()
        blockchain.add_new_block(new_block=new_block)
        send_node.broadcast_block(new_block)
    except BlockValidationException as e:
        return f'{e}', 400
    return "New block added", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
