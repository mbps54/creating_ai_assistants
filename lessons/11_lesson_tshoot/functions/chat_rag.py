import os
from datetime import datetime

import streamlit as st

import warnings
from langchain_core._api.deprecation import LangChainDeprecationWarning

# Suppress AgentExecutor deprecation warning
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage

from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ---------------------- HELPER FUNCTIONS ----------------------

def log_interaction(question: str, answer: str):
    """Saves the question and answer to ./history.log."""
    with open("./history.log", "a", encoding="utf-8") as f:
        f.write(f"\n--- {datetime.now().isoformat()} ---\n")
        f.write(f"User: {question}\n")
        f.write(f"Assistant: {answer}\n")


# ---------------------------- MAIN ----------------------------

def chat_rag_main():
    st.title("AI Assistant — Chat & RAG")

    # Model selection
    model_name = st.sidebar.selectbox(
        "Select a model::",
        ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4o"]
    )

    # Model initialization
    llm = init_chat_model(
        model_name,
        model_provider="openai",
        temperature=0.3,
    )

    # Message history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ---------------------- DOCUMENT LOADING ----------------------

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
                    st.session_state.retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
                    st.success("✅ Documents loaded.")
            else:
                st.warning("./docs is empty. Place .txt or .md files there.")

    # ---------------------- DISPLAYING HISTORY ----------------------

    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)

    # ---------------------- INPUT PROCESSING ----------------------

    if prompt := st.chat_input("Enter your question..."):
        user_msg = HumanMessage(content=prompt)
        st.chat_message("user").write(prompt)
        st.session_state.messages.append(user_msg)

        try:
            if "retriever" in st.session_state:
                # Convert messages to (question, answer) format
                chat_history = []
                last_user_msg = None
                for m in st.session_state.messages:
                    if isinstance(m, HumanMessage):
                        last_user_msg = m.content
                    elif isinstance(m, AIMessage) and last_user_msg:
                        chat_history.append((last_user_msg, m.content))
                        last_user_msg = None

                # RAG chain initialization
                qa_chain = ConversationalRetrievalChain.from_llm(
                    llm=llm,
                    retriever=st.session_state.retriever,
                    return_source_documents=True
                )

                result = qa_chain.invoke({
                    "question": prompt,
                    "chat_history": chat_history
                })

                answer = result.get("answer", "(no answer)")
                st.chat_message("assistant").write(answer)
                st.session_state.messages.append(AIMessage(content=answer))

                # Log only the question and answer
                log_interaction(prompt, answer)

                # Display sources
                sources = result.get("source_documents", [])
                if sources:
                    with st.expander("Sources:"):
                        for i, doc in enumerate(sources, 1):
                            filename = doc.metadata.get("source", "unknown file")
                            st.markdown(f"**Source {i}: `{filename}`**")
            else:
                st.warning("Please load the documents first.")
        except Exception as e:
            error_msg = f"Error: {e}"
            st.chat_message("assistant").write(error_msg)
            st.session_state.messages.append(AIMessage(content=error_msg))