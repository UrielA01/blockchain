import json
import os
from typing import List

__file__ = os.path.abspath('../doc/mem_pool.json')
def store_transactions_in_memory(transactions: List[dict]):
    text = json.dumps(transactions, indent=4)
    with open(__file__, "w") as file_obj:
        file_obj.write(text)

def get_transactions_from_memory() -> List[dict]:
    with open(__file__, "r") as file_obj:
        current_mem_pool_str = file_obj.read()
        current_mem_pool_list = json.loads(current_mem_pool_str)
    return current_mem_pool_list

store_transactions_in_memory([{"transaction": "bla"}, {"transaction": "bla"}, {"transaction": "bla"}])
print(get_transactions_from_memory())
print(type(get_transactions_from_memory()))
