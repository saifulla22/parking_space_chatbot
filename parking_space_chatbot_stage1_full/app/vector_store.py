from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings

def create_vector_db():
    loader = TextLoader('data/parking_info.txt')
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    embeddings = OllamaEmbeddings(model='llama3')

    Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory='./chroma_db'
    )

if __name__ == '__main__':
    create_vector_db()
