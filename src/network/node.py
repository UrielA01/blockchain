import json
from typing import List

import requests

from src.core.blockchain import Blockchain
from src.core.script import StackScript
from src.core.transaction import Transaction, TransactionInput, TransactionOutput
from src.wallet.wallet import Wallet


class Node:
    def __init__(self):
        ip = "127.0.0.1"
        port = 5000
        self.base_url = f"http://{ip}:{port}/"
        self.wallet = Wallet()

    def send(self, transaction_data: dict) -> requests.Response:
        url = f"{self.base_url}transactions"
        req_return = requests.post(url, json=transaction_data)
        req_return.raise_for_status()
        return req_return

    def process_transaction(self, inputs: List[TransactionInput], outputs: List[TransactionOutput]) -> requests.Response:
        transaction = Transaction(inputs=inputs, outputs=outputs)
        transaction.sign_inputs(self.wallet)
        return self.send({"transaction": transaction.to_dict})


class OtherNode:
    def __init__(self, ip: str, port: int):
        self.base_url = f"http://{ip}:{port}/"

    def send(self, transaction_data: dict) -> requests.Response:
        url = f"{self.base_url}transactions"
        req_return = requests.post(url, json=transaction_data)
        req_return.raise_for_status()
        return req_return


class ReceiveNode:
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain
        self.transaction_data: dict = {}
        self.inputs = {}
        self.outputs = {}

    def receive(self, transaction: dict):
        self.transaction_data = transaction
        self.inputs = transaction["inputs"]
        self.outputs = transaction["outputs"]

    def get_transaction_from_utxo(self, utxo_hash: str) -> Transaction:
        current_block = self.blockchain.last_block
        while current_block:
            if utxo_hash == current_block.transactions.hash:
                return current_block.transactions
            current_block = current_block.previous_block

    def get_locking_script_from_utxo(self, utxo_hash: str, utxo_index: int):
        transaction = self.get_transaction_from_utxo(utxo_hash)
        return transaction.outputs[utxo_index].locking_script

    def get_total_amount_in_inputs(self) -> int:
        total_in = 0
        for tx_input in self.inputs:
            input_dict = json.loads(tx_input)
            transaction = self.get_transaction_from_utxo(
                input_dict["transaction_hash"])
            utxo_amount = transaction.outputs[input_dict["output_index"]].amount
            total_in = total_in + utxo_amount
        return total_in

    def get_total_amount_in_outputs(self) -> int:
        total_out = 0
        for tx_output in self.outputs:
            output_dict = json.loads(tx_output)
            amount = output_dict["amount"]
            total_out = total_out + amount
        return total_out

    def validate_funds(self):
        assert self.get_total_amount_in_inputs() == self.get_total_amount_in_outputs()

    def validate_transaction(self):
        for tx_input in self.inputs:
            input_as_type = TransactionInput(transaction_hash=tx_input["transaction_hash"], output_index=tx_input["output_index"])
            locking_script = self.get_locking_script_from_utxo(
                input_as_type.transaction_hash, input_as_type.output_index)
            transaction_bytes = json.dumps(
            self.transaction_data, indent=2).encode('utf-8')
            unlock_stack_script = StackScript(tx_input["unlocking_script"], transaction_bytes)
            lock_stack_script = StackScript(locking_script, transaction_bytes)
            unlock_stack_script.execute()
            lock_stack_script.execute()

    def broadcast(self):
        node_list = [OtherNode("127.0.0.1", 5001),
                     OtherNode("127.0.0.1", 5002)]
        for node in node_list:
            try:
                node.send(self.transaction_data)
            except requests.ConnectionError:
                pass
