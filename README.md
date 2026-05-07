# RAG-Chatbot

A chatbot built with LangGraph and Google Gemini that answers questions using retrieval-augmented generation (RAG).

**Current Status**: Basic Q&A implementation. RAG features (PDF upload, vector store, retrieval) are planned but not yet implemented.

## Setup & Installation

```bash
# Clone and navigate to project
cd RAG-Chatbot

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file with your API keys:

```env
GOOGLE_API_KEY=your_google_api_key_here

# Optional: LangSmith tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_PROJECT=RAG-Chatbot
```

## Usage

### Run the Streamlit Web UI (Recommended)
```bash
streamlit run app.py
```

The web interface will open at http://localhost:8501 with:
- Chat interface for asking questions
- Chat history
- PDF upload button (for future RAG implementation)

### Run the CLI version
```bash
python main.py
```

### Run with LangGraph Studio
```bash
langgraph dev
```

The LangGraph Studio UI will be available at http://localhost:8123

## Project Structure

```
RAG-Chatbot/
├── app.py                     # Streamlit web UI
├── main.py                    # CLI entry point
├── requirements.txt           # Dependencies
├── langgraph.json            # LangGraph configuration
├── .env                       # Environment variables (not in git)
└── app/
    ├── __init__.py
    ├── config/               # Configuration management
    │   ├── __init__.py
    │   └── config.py         # Settings class
    ├── llm/                  # LLM initialization
    │   ├── __init__.py
    │   └── models.py         # Gemini model setup
    └── graph/                # LangGraph state machine
        ├── __init__.py
        ├── state.py          # State definition
        ├── nodes.py          # Node implementations
        ├── edges.py          # Edge routing logic
        └── graph_builder.py  # Graph construction
```

## Development

See [DESIGN.md](DESIGN.md) for architecture details and planned enhancements.

## License

MIT License - see [LICENSE](LICENSE) file for details.
