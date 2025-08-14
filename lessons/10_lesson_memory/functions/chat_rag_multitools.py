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
    lookup_docs(query: str) -> str

    Searches internal documentation for IP addresses, hostnames, descriptions, etc.
    Use if cmdb() did not return an IP.

    Argument:
    - query: IP, hostname, or keyword. For example, “BI” or “asw1”
    """
    if retriever is None:
        raise ToolException("Knowledge base not loaded.")
    docs = retriever.invoke(query)
    if not docs:
        raise ToolException("Nothing found in documentation.")
    return "\n\n".join(doc.page_content for doc in docs)


class PingInput(BaseModel):
    ip: str = Field(..., description="Device IPv4 address")

@tool(args_schema=PingInput)
def ping_tool(ip: str) -> bool:
    """
    Checks IP address availability via ping.
    Used only when a valid IP address is provided.
    """
    ipaddress.IPv4Address(ip)
    return ping(ip)

class CmdbInput(BaseModel):
    name: str = Field(..., description="Device name (hostname)")

@tool(args_schema=CmdbInput)
def cmdb_tool(name: str) -> str:
    """
    Retrieves the IP address by device name from CMDB.
    If IP is not found — use lookup_docs().
    """
    ip = cmdb(name)
    if not ip:
        raise ToolException(f"IP address for {name} not found in CMDB.")
    return ip

class ShowVlanPortInput(BaseModel):
    ip: str = Field(..., description="Device IP address")
    port: str = Field(..., description="Port name (e.g., Gi0/1)")

@tool(args_schema=ShowVlanPortInput)
def show_vlan_port_tool(ip: str, port: str) -> str:
    """
    Shows the VLAN configured on a specific network device port.
    Requires IP address and port name.
    """
    ipaddress.IPv4Address(ip)
    return show_vlan_port(ip, port)

class ShowAllPortsInput(BaseModel):
    ip: str = Field(..., description="Device IP address")

@tool(args_schema=ShowAllPortsInput)
def show_vlan_ports_all_tool(ip: str) -> str:
    """
    Shows a list of all device ports with corresponding VLANs.
    Requires device IP address.
    """
    ipaddress.IPv4Address(ip)
    return show_vlan_ports_all(ip)

class ChangeVlanInput(BaseModel):
    ip: str = Field(..., description="Device IP address")
    port: str = Field(..., description="Port name (e.g., Gi0/1)")
    vlan: int = Field(..., description="VLAN number (for example, 10)")

@tool(args_schema=ChangeVlanInput)
def change_vlan_tool(ip: str, port: str, vlan: int) -> str:
    """
    Changes VLAN on the specified device port.
    Requires IP address, port name, and VLAN number.
    """
    ipaddress.IPv4Address(ip)
    return change_vlan(ip, port, vlan)

# ---------------------------- SETUP ----------------------------

retriever = None

# --------------------------- PROMPT ---------------------------

def build_prompt_with_system_prompt(user_input: str) -> str:
    """
    Generates a request text with a system message and the current user input.
    """
    system_prompt = (
        "You are an assistant in a corporate IT infrastructure.\n"
        "If the request specifies a device name (e.g., ‘asw1’) but no IP:\n"
        "1. First call cmdb_tool() to get the IP by name.\n"
        "2. If cmdb_tool() did not return a result — call lookup_docs().\n"
        "Never make up an IP address — only use cmdb_tool() or lookup_docs().\n"
        "RAG with corporate documents and reference information is available via lookup_docs().\n"
        "Respond strictly based on internal documentation data.\n"
        "Respond briefly and to the point.\n"
        "Do not answer in Markdown format, answer in easy-to-read plain text.\n"
        "If listing commands, write each command on a new line."
    )
    return f"Sytem Messqge]: {system_prompt}\n[User]: {user_input}"


# ---------------------------- MAIN ----------------------------

def chat_rag_multitools_main():
    global retriever

    st.title("AI Assistant — Chat & RAG & Multitools")

    model_name = st.sidebar.selectbox(
        "Select model:",
        ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4o"]
    )

    llm = init_chat_model(model_name, model_provider="openai", temperature=0.3)

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
                    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
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
            cmdb_tool,
        ]

        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
        )

        try:
            full_prompt = build_prompt_with_system_prompt(prompt)
            print(f"Full prompt:\n{full_prompt}\n")
            result = agent.invoke({"input": full_prompt})
            answer = result.get("output", "(no answer)")
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
