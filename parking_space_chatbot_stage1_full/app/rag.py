from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama

def ask_question(question):
    embeddings = OllamaEmbeddings(model='llama3')
    db = Chroma(
        persist_directory='./chroma_db',
        embedding_function=embeddings
    )

    docs = db.similarity_search(question, k=3)
    context = '\n'.join([d.page_content for d in docs])

    llm = Ollama(model='llama3')
    prompt = f'Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer using only context.'
    return llm.invoke(prompt)
