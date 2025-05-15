import os
from dotenv import load_dotenv
from uuid import uuid4
from rich.pretty import pprint
from llama_stack_client import LlamaStackClient
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger as AgentEventLogger
from llama_stack_client.types import Document as RAGDocument

load_dotenv()

LLAMA_STACK_SERVER=os.getenv("LLAMA_STACK_SERVER")
INFERENCE_MODEL=os.getenv("INFERENCE_MODEL")

print(f"LLAMA_STACK_SERVER: {LLAMA_STACK_SERVER}")
print(f"INFERENCE_MODEL: {INFERENCE_MODEL}")

client = LlamaStackClient(
    base_url=LLAMA_STACK_SERVER
)

vector_db_id = "ragged-db"

user_query = "What is the Grand Invention?"

rag_response = client.tool_runtime.rag_tool.query(content=user_query, 
                                                  vector_db_ids=[vector_db_id])


messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {
        "role": "user",
        "content": f""" 
        Answer the question based on the context provided.
        Context: {rag_response.content}
        Question: {user_query} 
        """,
    },
]

completion = client.chat.completions.create(
    model=INFERENCE_MODEL,
    messages=messages,
    temperature=0.1, 
)

response = completion.choices[0].message.content
print(f"{user_query}: ", response)
