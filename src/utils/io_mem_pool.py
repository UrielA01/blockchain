import json
import os
from typing import List

mem_pool_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../mem_pools/transactions.json'))

def get_transactions_from_memory() -> List[dict]:
    with open(mem_pool_path, "r") as file_obj:
        current_mem_pool_str = file_obj.read()
        current_mem_pool_list = json.loads(current_mem_pool_str)
    return current_mem_pool_list

def store_transactions_in_memory(transactions: List[dict]):
    current_transactions = get_transactions_from_memory()
    for transaction in transactions:
        current_transactions.append(transaction)
    text = json.dumps(current_transactions, indent=4)
    with open(mem_pool_path, "w") as file_obj:
        file_obj.write(text)

def reset_transaction_memory():
    text = json.dumps([], indent=4)
    with open(mem_pool_path, "w") as file_obj:
        file_obj.write(text)


