import os
import ipaddress

import streamlit as st
from pydantic import BaseModel, Field

import warnings
from langchain_core._api.deprecation import LangChainDeprecationWarning

# Suppress AgentExecutor deprecation warning
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import ToolException, tool

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from tools.ping import ping
from tools.cmdb import cmdb
from tools.show_vlan_port import show_vlan_port
from tools.show_vlan_ports_all import show_vlan_ports_all
from tools.change_vlan import change_vlan


# ---------------------------- TOOLS ----------------------------

@tool
def lookup_docs(query: str) -> str:
    """
    Searches for information in internal documentation:
    IP addresses, hostnames, descriptions, etc.

    Argument:
    - query: IP, hostname, or keyword. For example, “BI” or “asw1”
    """
    if retriever is None:
        raise ToolException("Knowledge base is not loaded.")
    docs = retriever.invoke(query)
    if not docs:
        raise ToolException("Nothing found in the documentation.")
    return "\n\n".join(doc.page_content for doc in docs)


class PingInput(BaseModel):
    ip: str = Field(..., description="IPv4 address of the device")

@tool(args_schema=PingInput)
def ping_tool(ip: str) -> bool:
    """
    Checks the availability of an IP address via ping.
    Used only when a valid IP address is provided.
    """
    ipaddress.IPv4Address(ip)
    return ping(ip)

class CmdbInput(BaseModel):
    name: str = Field(..., description="Device name (hostname)")

@tool(args_schema=CmdbInput)
def cmdb_tool(name: str) -> str:
    """
    Retrieves the IP address of a device by name from the CMDB.
    If the IP is not found — use lookup_docs().
    """
    ip = cmdb(name)
    if not ip:
        raise ToolException(f"IP address for {name} not found in CMDB.")
    return ip

class ShowVlanPortInput(BaseModel):
    ip: str = Field(..., description="Device IP address")
    port: str = Field(..., description="Port name (for example, Gi0/1)")

@tool(args_schema=ShowVlanPortInput)
def show_vlan_port_tool(ip: str, port: str) -> str:
    """
    Shows the VLAN configured on a specific port of the network device.
    Requires IP address and port name.
    """
    ipaddress.IPv4Address(ip)
    return show_vlan_port(ip, port)

class ShowAllPortsInput(BaseModel):
    ip: str = Field(..., description="Device IP address")

@tool(args_schema=ShowAllPortsInput)
def show_vlan_ports_all_tool(ip: str) -> str:
    """
    Displays a list of all ports on the device with their corresponding VLANs.
    Requires the IP address of the device.
    """
    ipaddress.IPv4Address(ip)
    return show_vlan_ports_all(ip)

class ChangeVlanInput(BaseModel):
    ip: str = Field(..., description="Device IP address")
    port: str = Field(..., description="Port name (for example, Gi0/1)")
    vlan: int = Field(..., description="VLAN number (for example, 10)")

@tool(args_schema=ChangeVlanInput)
def change_vlan_tool(ip: str, port: str, vlan: int) -> str:
    """
    Changes the VLAN on the specified port of the device.
    Requires IP address, port name, and VLAN number.
    """
    ipaddress.IPv4Address(ip)
    return change_vlan(ip, port, vlan)


# ---------------------------- SETUP ----------------------------

retriever = None


def build_prompt_from_history(messages, system_prompt: str) -> str:
    """
    Creates a request text for the agent from the message history and the current input.
    """
    lines = [f"[System message]: {system_prompt}"]
    for msg in messages:
        if isinstance(msg, HumanMessage):
            lines.append(f"User: {msg.content}")
        elif hasattr(msg, "name") and msg.name == "assistant":
            lines.append(f"Assistant: {msg.content}")
    #lines.append(f"User: {new_user_input}\n")
    return "\n".join(lines)


# ---------------------------- MAIN ----------------------------

def chat_rag_multitools_memory_main():
    global retriever

    st.title("AI Assistant — Chat & RAG & Multitools & Memory")

    model_name = st.sidebar.selectbox(
        "Select model:",
        ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4o"]
    )

    llm = init_chat_model(model_name, model_provider="openai", temperature=0.3)

    system_prompt = (
        "You are an assistant in a corporate IT infrastructure.\n"
        "If the request specifies a device name (for example, ‘asw1’) but no IP address, then:\n"
        "1. First, call cmdb_tool() to obtain the IP by name.\n"
        "2. If cmdb_tool() did not return a result — call lookup_docs().\n"
        "Never make up an IP address — only obtain it via cmdb_tool() or lookup_docs().\n"
        "RAG with corporate documents and reference information is available via lookup_docs().\n"
        "Respond strictly based on internal documentation data\n"
        "Respond briefly and to the point.\n"
        "Do not respond in Markdown format, respond in easy-to-read text.\n"
        "If you list commands, write each command on a new line."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.expander("Load documents for RAG"):
        if st.button("Index ./docs"):
            docs_path = "./docs"
            if os.path.exists(docs_path) and os.listdir(docs_path):
                with st.spinner("Indexing documents..."):
                    loader = DirectoryLoader(
                        docs_path,
                        loader_cls=TextLoader,
                        show_progress=True
                    )
                    documents = loader.load()
                    splitter = RecursiveCharacterTextSplitter(
                        chunk_size=1000,
                        chunk_overlap=200
                    )
                    splits = splitter.split_documents(documents)
                    embeddings = OpenAIEmbeddings()
                    vectorstore = FAISS.from_documents(splits, embeddings)
                    retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
                    st.session_state.retriever = retriever
                    st.success("✅ Loaded and indexed")
            else:
                st.warning("The ./docs directory is empty")

    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)
        elif hasattr(msg, "name") and msg.name == "assistant":
            st.chat_message("assistant").write(msg.content)

    if prompt := st.chat_input("Enter your question..."):
        user_msg = HumanMessage(content=prompt)
        st.chat_message("user").write(user_msg.content)
        st.session_state.messages.append(user_msg)

        tools = [
            lookup_docs,
            ping_tool,
            show_vlan_port_tool,
            show_vlan_ports_all_tool,
            change_vlan_tool,
            cmdb_tool
        ]

        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION
        )

        try:
            full_prompt = build_prompt_from_history(
                messages=st.session_state.messages,
                system_prompt=system_prompt
            )
            print(f"\n\n==> full prompt:\n{full_prompt}")
            result = agent.invoke({"input": full_prompt})
            answer = result.get("output", "(no response)")
            st.chat_message("assistant").write(answer)
            st.session_state.messages.append(
                SystemMessage(name="assistant", content=answer)
            )
        except Exception as e:
            error_msg = f"Agent error: {e}"
            st.chat_message("assistant").write(error_msg)
            st.session_state.messages.append(
                SystemMessage(name="assistant", content=error_msg)
            )