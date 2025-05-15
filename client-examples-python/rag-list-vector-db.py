import os
from dotenv import load_dotenv
from uuid import uuid4
from rich.pretty import pprint
from llama_stack_client import LlamaStackClient
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger as AgentEventLogger

load_dotenv()

LLAMA_STACK_SERVER=os.getenv("LLAMA_STACK_SERVER")
INFERENCE_MODEL=os.getenv("INFERENCE_MODEL")

pprint(f"LLAMA_STACK_SERVER: {LLAMA_STACK_SERVER}")
pprint(f"INFERENCE_MODEL: {INFERENCE_MODEL}")

client = LlamaStackClient(
    base_url=LLAMA_STACK_SERVER
)

vector_dbs = client.vector_dbs.list()
for vector_db in vector_dbs:
    pprint(f"Vector DB: {vector_db.identifier}")    


providers = client.providers.list()


for provider in providers: 
    if provider.api == "vector_io":
      pprint(f"Vector DB Provider: {provider.provider_id}")

      