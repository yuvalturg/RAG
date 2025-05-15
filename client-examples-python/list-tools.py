import os
from llama_stack_client import LlamaStackClient
from rich.pretty import pprint
from dotenv import load_dotenv

load_dotenv()


LLAMA_STACK_SERVER=os.getenv("LLAMA_STACK_SERVER")
INFERENCE_MODEL=os.getenv("INFERENCE_MODEL")

print(LLAMA_STACK_SERVER)
print(INFERENCE_MODEL)

client = LlamaStackClient(
    base_url=LLAMA_STACK_SERVER
)


for toolgroup in client.toolgroups.list():
    pprint(toolgroup)
