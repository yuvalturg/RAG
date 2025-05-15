from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

LLAMA_STACK_SERVER_OPENAI = os.getenv("LLAMA_STACK_SERVER_OPENAI")
API_KEY="not applicable"

print("LLAMA_STACK_SERVER: ", LLAMA_STACK_SERVER_OPENAI)

if LLAMA_STACK_SERVER_OPENAI is None:
    raise ValueError("LLAMA_STACK_SERVER_OPENAI environment variable not set")

client = OpenAI(
    api_key=API_KEY,
    base_url=LLAMA_STACK_SERVER_OPENAI
    )

# List available models
models = client.models.list()

# Print model IDs
for model in models.data:
    print(model.id)

