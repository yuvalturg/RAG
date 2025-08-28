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

vector_db_id = f"ragged-db"
provider_id = "pgvector" # or "faiss"
vector_db = client.vector_dbs.register(
    vector_db_id=vector_db_id,
    embedding_dimension=384,
    embedding_model="all-MiniLM-L6-v2",
    provider_id=provider_id
)

print(f"Creating Vector DB ID: {vector_db_id} for provider {provider_id}")

urls = [
  "https://raw.githubusercontent.com/rh-ai-quickstart/RAG/d504f01c0ade8988a217abc856a6ab41f915a537/notebooks/Zippity_Zoo_Grand_Invention.pdf"
]

documents = [
    RAGDocument(
        document_id=f"num-{i}",
        content=url,
        mime_type="application/pdf",
        metadata={},
    )
    for i, (url) in enumerate(urls)
]

print(f"Loading Documents: {documents}")

# Insert documents into the vector database
client.tool_runtime.rag_tool.insert(
    documents=documents,
    vector_db_id=vector_db_id,
    chunk_size_in_tokens=512,
)

print(f"Created Vector DB ID: {vector_db_id} for provider {provider_id}")

