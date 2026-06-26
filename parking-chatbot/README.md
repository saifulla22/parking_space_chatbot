# Parking Reservation Chatbot

An intelligent chatbot for parking space reservations built with **LangChain**, **LangGraph**, **ChromaDB**, and **HuggingFace LLMs**.

## Architecture

| Stage | Description |
|-------|-------------|
| Stage 1 | RAG chatbot (ChromaDB + guardrails + evaluation) |
| Stage 2 | Human-in-the-loop admin approval via console |
| Stage 3 | MCP-style reservation file writer |
| Stage 4 | LangGraph orchestration of all stages |

## Project Structure

```
parking-chatbot/
├── llm/                    # HuggingFace LLM wrapper + LangChain adapter
├── data/                   # Static parking info (txt) + dynamic data (SQLite)
├── stage1_rag/             # RAG system, chatbot, guardrails, evaluation
├── stage2_hitl/            # Human-in-the-loop admin agent (console)
├── stage3_mcp/             # Reservation file writer
├── stage4_graph/           # LangGraph orchestration
└── tests/                  # pytest test suites (2+ tests per module)
```

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Stage 1 — RAG Chatbot only
```bash
python -m stage1_rag.chatbot
```

### 3. Run Full Pipeline — Stage 4 (all stages)
```bash
python -m stage4_graph.graph
```

### 4. Run RAG Evaluation
```bash
python -m stage1_rag.evaluation
```

### 5. Run Tests
```bash
pytest tests/ -v
```

## Runtime Notes

- **ChromaDB** persists to `./chroma_db/` on first run. The `all-MiniLM-L6-v2` embedding model (~80MB) downloads automatically via `sentence-transformers`.
- **Reservations** are written to `confirmed_reservations.txt`.
- **SQLite** database saved to `parking.db` (availability, prices, hours).
- **Admin approval** is via console input — the terminal will prompt `approve` / `reject` when a reservation is ready.

## LLM Configuration

The project uses the HuggingFace Inference Router (OpenAI-compatible API). Model and key are set in `llm/llm_client.py`.
