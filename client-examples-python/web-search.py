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

print(f"LLAMA_STACK_SERVER: {LLAMA_STACK_SERVER}")
print(f"INFERENCE_MODEL: {INFERENCE_MODEL}")

client = LlamaStackClient(
    base_url=LLAMA_STACK_SERVER
)


agent = Agent(
    client,
    model=INFERENCE_MODEL,  # or another valid model identifier
    instructions="You are a helpful assistant.",  # system prompt instructions for the agent
    tools=["builtin::websearch"],
    input_shields=[],
    output_shields=[],
    enable_session_persistence=False
)

session_id = agent.create_session(f"test-session-{uuid4()}")


response = agent.create_turn(
    messages=[
        {
            "role": "user",
            "content": "Who won the 2025 Super Bowl?",
        }
    ],    
    session_id=session_id,
)

pprint(f"response: {response}")

for log in AgentEventLogger().log(response):
    log.print()


response = agent.create_turn(
    messages=[
        {
            "role": "user",
            "content": "Who is the current US President?",
        }
    ],    
    session_id=session_id,
)

pprint(f"response: {response}")

for log in AgentEventLogger().log(response):
    log.print()


