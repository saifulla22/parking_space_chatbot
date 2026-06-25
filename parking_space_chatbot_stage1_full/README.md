# Parking Space Chatbot - Stage 1

## Installation

1. Install Python 3.11+
2. Install Ollama: https://ollama.com
3. Pull model:

```bash
ollama pull llama3
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Create vector database:

```bash
python app/vector_store.py
```

6. Run chatbot:

```bash
python app/chatbot.py
```

## Features

- RAG chatbot
- ChromaDB vector store
- Ollama Llama3
- Guardrails
- Pytest tests
