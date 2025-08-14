#!/usr/bin/env python

import warnings

from langchain_core._api.deprecation import LangChainDeprecationWarning

warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationTokenBufferMemory

from tools.ping import ping


# ---------------------------- TOOLS ----------------------------

@tool
def ping_tool(host: str) -> bool:
    """Ping a host to check if it's reachable. Returns True or False."""
    return ping(host)


# ---------------------------- SETUP ----------------------------

tools = [ping_tool]

# Model initialization
llm = init_chat_model("gpt-4o-mini", model_provider="openai")

# Creating memory with a token limit
memory = ConversationTokenBufferMemory(
    llm=llm,
    max_token_limit=40,
    memory_key="chat_history",
    input_key="input",
    return_messages=True,
)

# System message — how to behave
memory.chat_memory.add_message(SystemMessage(content=(
    "You are a network engineer’s assistant. "
    "You can use the ping() command."
)))

# Initialize the agent with memory
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    handle_parsing_errors=True
)


# ---------------------------- DIALOG ----------------------------

inputs = [
    "Check if 8.8.8.8 is reachable via ping",
    "Once more",
    "and now check 8.8.4.4",
    "Once more",
    "Once more",
    "Once more",
    "Once more",
]

for prompt in inputs:
    print(f"==> question: {prompt}")
    response = agent.invoke({"input": prompt})
    print(f"==> answer: {response['output']}\n")