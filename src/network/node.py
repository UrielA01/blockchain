import copy
import json
from typing import List
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
import requests

from blockchain_utils.blockchain import Blockchain
from blockchain_utils.script import StackScript
from blockchain_utils.transaction import Transaction, TransactionInput, TransactionOutput
from utils.crypto_utils import calculate_ripemd160, calculate_sha256
from wallet.wallet import Wallet


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
        transaction = Transaction(owner=self, inputs=inputs, outputs=outputs)
        transaction.sign_inputs()
        return self.send({"transaction": transaction.tx_data_as_dict()})


class OtherNode:
    def __init__(self, ip: str, port: int):
        self.base_url = f"http://{ip}:{port}/"

    def send(self, transaction_data: dict) -> requests.Response:
        url = f"{self.base_url}transactions"
        req_return = requests.post(url, json=transaction_data)
        req_return.raise_for_status()
        return req_return


class NodeTransaction:
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain
        self.transaction_data: dict = {}
        self.inputs = ""
        self.outputs = ""

    def receive(self, transaction: dict):
        self.transaction_data = transaction
        self.inputs = transaction["inputs"]
        self.outputs = transaction["outputs"]

    def validate_transaction(self):
        for tx_input in self.inputs:
            input_dict = json.loads(tx_input)
            locking_script = self.get_locking_script_from_utxo(
                input_dict["transaction_hash"], input_dict["output_index"])
            self.execute_script(input_dict["unlocking_script"], locking_script)

    def get_locking_script_from_utxo(self, utxo_hash: str, utxo_index: int):
        transaction_data = self.get_transaction_from_utxo(utxo_hash)
        return json.loads(transaction_data["outputs"][utxo_index])["locking_script"]

    def validate_transaction_signature(self):
        transaction_data = copy.deepcopy(self.transaction_data)
        for count, tx_input in enumerate(transaction_data["inputs"]):
            tx_input_dict = json.loads(tx_input)
            public_key = tx_input_dict.pop("public_key")
            signature = tx_input_dict.pop("signature")
            transaction_data["inputs"][count] = json.dumps(tx_input_dict)
            transaction_bytes = json.dumps(
                transaction_data, indent=2).encode('utf-8')
            if not Wallet.valid_signature(signature, public_key, transaction_bytes):
                raise ValueError("Invalid signature")

    def get_transaction_from_utxo(self, utxo_hash: str) -> dict:
        current_block = self.blockchain.last_block
        while current_block:
            if utxo_hash == current_block.transaction_hash:
                return current_block.transaction_data
            current_block = current_block.previous_block

    def validate_funds_are_owned_by_sender(self):
        for tx_input in self.inputs:
            input_dict = json.loads(tx_input)
            public_key = input_dict["public_key"]
            sender_public_key_hash = calculate_ripemd160(calculate_sha256(
                public_key))
            transaction_data = self.get_transaction_from_utxo(
                input_dict["transaction_hash"])
            public_key_hash = json.loads(
                transaction_data["outputs"][input_dict["output_index"]])["public_key_hash"]
            assert public_key_hash == sender_public_key_hash

    def validate_funds(self):
        assert self.get_total_amount_in_inputs() == self.get_total_amount_in_outputs()

    def get_total_amount_in_inputs(self) -> int:
        total_in = 0
        for tx_input in self.inputs:
            input_dict = json.loads(tx_input)
            transaction_data = self.get_transaction_from_utxo(
                input_dict["transaction_hash"])
            utxo_amount = json.loads(
                transaction_data["outputs"][input_dict["output_index"]])["amount"]
            total_in = total_in + utxo_amount
        return total_in

    def get_total_amount_in_outputs(self) -> int:
        total_out = 0
        for tx_output in self.outputs:
            output_dict = json.loads(tx_output)
            amount = output_dict["amount"]
            total_out = total_out + amount
        return total_out

    def execute_script(self, unlocking_script: str, locking_script: str):
        unlocking_script_list = unlocking_script.split(" ")
        locking_script_list = locking_script.split(" ")
        stack_script = StackScript(self.transaction_data)
        for element in unlocking_script_list:
            if element.startswith("OP"):
                class_method = getattr(StackScript, element.lower())
                class_method(stack_script)
            else:
                stack_script.push(element)
        for element in locking_script_list:
            if element.startswith("OP"):
                class_method = getattr(StackScript, element.lower())
                class_method(stack_script)
            else:
                stack_script.push(element)

    def broadcast(self):
        node_list = [OtherNode("127.0.0.1", 5001),
                     OtherNode("127.0.0.1", 5002)]
        for node in node_list:
            try:
                node.send(self.transaction_data)
            except requests.ConnectionError:
                pass
