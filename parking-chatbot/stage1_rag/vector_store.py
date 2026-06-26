import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

CHROMA_DB_DIR = "./chroma_db"
COLLECTION_NAME = "parking_info"
# Small, fast model (~80MB). Downloads automatically on first run.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return the shared embedding model instance."""
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def build_vector_store(data_path: str = "data/parking_info.txt") -> Chroma:
    """
    Load parking info from a text file, split into chunks, embed,
    and persist to ChromaDB. Call once on first run.
    """
    loader = TextLoader(data_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    chunks = splitter.split_documents(documents)

    embeddings = get_embeddings()
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DB_DIR,
    )
    print(f"[VectorStore] Built with {len(chunks)} chunks from '{data_path}'.")
    return vector_store


def load_vector_store() -> Chroma:
    """Load an existing persisted ChromaDB vector store."""
    embeddings = get_embeddings()
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_DIR,
    )


def get_or_build_vector_store(data_path: str = "data/parking_info.txt") -> Chroma:
    """Load from disk if it exists, otherwise build from the text file."""
    if os.path.exists(CHROMA_DB_DIR):
        return load_vector_store()
    return build_vector_store(data_path)
