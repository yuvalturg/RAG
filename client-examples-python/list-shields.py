import os
from llama_stack_client import LlamaStackClient
from rich.pretty import pprint

LLAMA_STACK_SERVER=os.getenv("LLAMA_STACK_SERVER")

print(f"LLAMA_STACK_SERVER: {LLAMA_STACK_SERVER}")

client = LlamaStackClient(
    base_url=LLAMA_STACK_SERVER
)

for shield in client.shields.list():
    pprint(shield)

