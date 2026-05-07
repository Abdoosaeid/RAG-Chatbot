# RAG-Chatbot

A RAG-powered chatbot using LangGraph, Google Gemini, and CopilotKit. Upload PDFs and ask questions — the agent retrieves relevant passages and generates grounded answers.

## Architecture

```
PDF Upload → Text Extraction → Chunking → Google Embeddings → FAISS Vector Store → Retrieval Tool → Gemini LLM → Response
```

## Project Structure

```
RAG-Chatbot/
├── agent.py              # LangGraph agent + FastAPI server (AG-UI endpoint)
├── config.py             # Pydantic settings (API keys, LLM params)
├── models.py             # Gemini LLM initialization
├── rag.py                # PDF ingestion, embeddings, vector store, retriever tool
├── requirements.txt      # Python dependencies
├── langgraph.json        # LangGraph config
├── .env                  # Environment variables (not in git)
└── frontend/             # Next.js + CopilotKit UI
    ├── app/              # Pages and layout
    ├── package.json
    └── ...
```

## Setup

### Backend

```bash
python -m venv .venv
.venv/Scripts/activate      # Windows
# source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

### Configuration

Create a `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key_here

# Optional: LangSmith tracing
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_TRACING=true
LANGCHAIN_PROJECT=RAG-Chatbot
```

## Running

### Backend (FastAPI + LangGraph)

```bash
python agent.py
```

Server runs on `http://localhost:8123`

### Frontend (CopilotKit)

```bash
cd frontend
npm run dev
```

UI runs on `http://localhost:3000`

## Key Components

| File | Purpose |
|------|---------|
| `agent.py` | LangGraph state machine with FastAPI + AG-UI endpoint |
| `rag.py` | PDF → text → chunks → Google embeddings → FAISS → retriever tool |
| `config.py` | Centralized settings via Pydantic (`gemini-2.5-flash`) |
| `models.py` | Gemini chat model factory |

## License

MIT
