#!/usr/bin/env python

import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage

# Model name and system prompt
model_name = "gpt-4o-mini"
system_prompt = "You are an AI assistant. Respond briefly and to the point."

# Initialize the model
chat = init_chat_model(
    model_name,
    model_provider="openai",
    temperature=0.7,
)

# Page title
st.title("LLM Chat")

# Initialize the message history in the session
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add the system prompt as a LangChain object only during initialization
    st.session_state.messages.append(SystemMessage(content=system_prompt))

# Display the history (everything except the system message)
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif hasattr(msg, "name") and msg.name == "assistant":  # for compatibility
        st.chat_message("assistant").write(msg.content)

# User input
if prompt := st.chat_input("Enter your question..."):
    # Add the question to the history
    user_msg = HumanMessage(content=prompt)
    st.chat_message("user").write(user_msg.content)
    st.session_state.messages.append(user_msg)

    # Call the model
    response = chat.invoke(st.session_state.messages)

    # Display and save the response
    st.chat_message("assistant").write(response.content)
    st.session_state.messages.append(response)