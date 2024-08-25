from uuid import uuid4

from flask import Flask, request

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
