# Document Intelligence System

A **Multi-Agent Document Intelligence** platform powered by **GitHub Models (GPT-4o)**, ChromaDB, local embeddings, and Google ADK agents.

---

## Architecture

```
Frontend (React/Vite :3000)
       │
       │  REST API (axios)
       ▼
Backend (FastAPI :8000)
       │
       ├── GitHub Models API (GPT-4o) ← LLM
       ├── ChromaDB (local persistence) ← Vector store
       ├── sentence-transformers ← Embeddings (local)
       └── Google ADK Agents ← Orchestration
```

## Features

| Feature | Endpoint |
|---|---|
| Upload document (PDF/DOCX/TXT) | `POST /upload` |
| Concise summary | `POST /summary` `{"summary_type":"concise"}` |
| Detailed summary | `POST /summary` `{"summary_type":"detailed"}` |
| RAG Q&A | `POST /ask` |
| Extract insights | `POST /insights` |
| System health | `GET /health` |
| System stats | `GET /stats` |
| Reset database | `POST /database/reset` |

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Node.js 18+
- GitHub fine-grained personal access token ([create one here](https://github.com/settings/tokens))

### 2. Backend Setup

```bash
# Create and activate virtualenv
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env — fill in your GITHUB_TOKEN
```

### 3. Start the Backend

```bash
uvicorn app.api:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 4. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend available at: http://localhost:3000 (or :5173)

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `LLM_PROVIDER` | No | `github` (default) or `groq` |
| `GITHUB_TOKEN` | **Yes** (github) | GitHub fine-grained PAT |
| `GITHUB_MODEL` | No | Model name (default: `gpt-4o`) |
| `GROQ_API_KEY` | Yes (groq) | Groq API key (fallback) |
| `EMBEDDING_PROVIDER` | No | `openai` (default) or `local` |
| `EMBEDDING_MODEL` | No | Embedding model (default: `text-embedding-3-small`) |
| `CHROMA_PERSIST_DIR` | No | Vector DB path (default: `./chroma_db`) |

---

## Project Structure

```
ai-sdlc/
├── app/
│   ├── api.py              # FastAPI routes (upload, summary, ask, insights)
│   ├── runner.py           # Document processing orchestrator
│   ├── streamlit_app.py    # Optional Streamlit UI
│   ├── embeddings/         # Local embedding model wrapper
│   └── llm/
│       ├── github_provider.py   # GitHub Models provider (default)
│       ├── groq_provider.py     # Groq provider (fallback)
│       ├── provider_factory.py  # Factory / singleton
│       └── base.py             # Abstract base class
├── agents/                 # Google ADK agents
│   ├── orchestrator_agent.py
│   ├── extractor_agent.py
│   ├── summarizer_agent.py
│   ├── insights_agent.py
│   └── qa_agent.py
├── utils/
│   ├── config.py           # Centralized env config
│   ├── llm_client.py       # High-level LLM helpers
│   ├── chroma_manager.py   # ChromaDB CRUD
│   └── document_processor.py
├── frontend/               # React + Vite frontend
│   └── src/
│       ├── pages/          # Upload, Dashboard, Chat, Status
│       ├── components/     # Reusable UI components
│       └── services/       # API client (axios)
├── tests/                  # Pytest suite
├── .env                    # Local secrets (git-ignored)
├── .env.example            # Template
└── requirements.txt
```

---

## Deployment (Production)

### Backend (any Python host — Railway, Render, EC2)

```bash
pip install -r requirements.txt
uvicorn app.api:app --host 0.0.0.0 --port 8000
```

Set all environment variables in your host's dashboard.

### Frontend (Vercel / Netlify / static)

```bash
cd frontend
npm run build          # outputs to frontend/dist/
```

Set `VITE_API_URL` to your deployed backend URL before building:
```bash
VITE_API_URL=https://your-backend.railway.app npm run build
```

---

## API Reference

Full interactive docs: http://localhost:8000/docs (Swagger UI)

### Upload Document
```http
POST /upload
Content-Type: multipart/form-data
file: <binary>
```

### Ask Question
```http
POST /ask
Content-Type: application/json
{"doc_id": "abc123", "question": "What is the main topic?"}
```

### Generate Summary
```http
POST /summary
Content-Type: application/json
{"doc_id": "abc123", "summary_type": "concise"}
```
