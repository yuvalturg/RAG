import os
from llama_stack_client import LlamaStackClient

LLAMA_STACK_SERVER=os.getenv("LLAMA_STACK_SERVER")

print(f"LLAMA_STACK_SERVER: {LLAMA_STACK_SERVER}")

client = LlamaStackClient(
    base_url=LLAMA_STACK_SERVER
)

shield_id = "content_safety"
client.shields.register(shield_id=shield_id, provider_shield_id="meta-llama/Llama-Guard-3-8B")


