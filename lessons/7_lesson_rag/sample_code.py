from langchain.chat_models import init_chat_model
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Load documents
loader = TextLoader("./docs/corporate_wiki.md")
documents = loader.load()

# 2. Index documents
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever()

# 3. Initialize the LLM
llm = init_chat_model("gpt-4o-mini", model_provider="openai")

# 4. Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a network engineer’s assistant. Respond based on the documentation."),
    ("human", "Context:\n{context}\n\nQuestion: {question}")
])

# 5. Question
question = "How do I arrange a business trip?"

# 6. Create an LCEL chain
rag_chain = (
    {"context": retriever, "question": lambda x: x}
    | prompt
    | llm
    | StrOutputParser()
)

# 7. Run the chain
response = rag_chain.invoke(question)
print(response)

# 8. Debug — inspect the actual prompt
docs = retriever.invoke(question)
context_text = "\n\n".join([doc.page_content for doc in docs])
prompt_value = prompt.format_prompt(context=context_text, question=question)
print("\n==> Generated prompt:\n")
print(prompt_value.to_string())

# 9. Sources
print("\nSources used:")
for i, doc in enumerate(docs, 1):
    source = doc.metadata.get("source", "unknown file")
    print(f"  - document {i}: {source}")