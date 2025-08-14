#!/usr/bin/env python

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain.agents import initialize_agent
from tools.ping import ping

# 1. Ping tool
@tool
def ping_tool(host: str) -> bool:
    """Checks IP address reachability via ping."""
    return ping(host)

# 2. Define the list of tools
tools = [ping_tool]

# 3. Initialize the model
llm = init_chat_model("gpt-4o-mini", model_provider="openai")

# 4. Initialize the agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    verbose=True
)

# 5. Run the agent
response = agent.invoke({"input": "Check if 8.8.8.8 is reachable via ping"})
print(f"==> response: {response['output']}\n")
print("\n---\n")
response = agent.invoke({"input": "Check if 192.168.8.1 is reachable via ping"})
print(f"==> response: {response['output']}\n")
