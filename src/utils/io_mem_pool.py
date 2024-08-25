import json
import os
from typing import List

mem_pool_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../doc/mem_pool.json'))
def store_transactions_in_memory(transactions: List[dict]):
    text = json.dumps(transactions, indent=4)
    with open(mem_pool_path, "w") as file_obj:
        file_obj.write(text)

def get_transactions_from_memory() -> List[dict]:
    with open(mem_pool_path, "r") as file_obj:
        current_mem_pool_str = file_obj.read()
        current_mem_pool_list = json.loads(current_mem_pool_str)
    return current_mem_pool_list
