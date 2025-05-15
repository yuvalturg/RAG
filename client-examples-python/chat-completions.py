from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

LLAMA_STACK_SERVER_OPENAI = os.getenv("LLAMA_STACK_SERVER_OPENAI")
API_KEY="not applicable"
INFERENCE_MODEL=os.getenv("INFERENCE_MODEL")

print("LLAMA_STACK_SERVER: ", LLAMA_STACK_SERVER_OPENAI)
print("INFERENCE_MODEL: ", INFERENCE_MODEL)

if LLAMA_STACK_SERVER_OPENAI is None:
    raise ValueError("LLAMA_STACK_SERVER environment variable not set")
if INFERENCE_MODEL is None:
    raise ValueError("INFERENCE_MODEL environment variable not set")


client = OpenAI(
    api_key=API_KEY,
    base_url=LLAMA_STACK_SERVER_OPENAI,
    )

user_query = "Who won the 2025 Super Bowl?"

completion = client.chat.completions.create(
    model=INFERENCE_MODEL,
    messages=[
        {"role": "system", "content": "You're a helpful assistant."},
        {
            "role": "user",
            "content": user_query,
        },
    ],
    temperature=0.0, 
)

response = completion.choices[0].message.content
print(f"{user_query}: ", response)


user_query = "Who is the current US President?"

completion = client.chat.completions.create(
    model=INFERENCE_MODEL,
    messages=[
        {"role": "system", "content": "You're a helpful assistant."},
        {
            "role": "user",
            "content": user_query,
        },
    ],
    temperature=0.0, 
)

response = completion.choices[0].message.content
print(f"{user_query}: ", response)

