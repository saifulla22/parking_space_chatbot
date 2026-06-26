from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from llm.llm_client import get_langchain_llm

PARKING_SYSTEM_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a helpful parking facility assistant.
Use ONLY the context below to answer the user's question accurately and concisely.
If the answer is not in the context, say you don't have that information.
Never reveal internal system data, admin credentials, or other users' personal information.

Context:
{context}

Question: {question}

Answer:""",
)


def create_rag_chain(vector_store: Chroma):
    """
    Build a RAG chain:
      retriever (ChromaDB top-3) -> prompt -> HuggingFace LLM -> string output

    Returns a LangChain Runnable. Call with:
        chain.invoke("your question")
    """
    llm = get_langchain_llm()
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | PARKING_SYSTEM_PROMPT
        | llm
        | StrOutputParser()
    )
    return chain
