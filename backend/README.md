# Scripts Writer — Backend

Agentic AI pipeline for generating high-converting video scripts and marketing posts.

## Quick Start

For a complete setup guide including the frontend and dev script, see the [root README](../README.md).

```bash
# From the backend/ directory

# 1. Install dependencies (creates .venv automatically)
uv sync

# 2. Copy environment config and fill in your API keys
cp ../.env.example .env
# Edit .env with your API keys (at least one LLM provider)

# 3. Start the dev server
uv run uvicorn app.main:app --reload
```

Or use the root `dev.sh` script to run both backend and frontend:

```bash
../dev.sh start
```

The server starts at **http://localhost:8000**.

Verify it's running:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

API docs available at **http://localhost:8000/docs**.

## Environment Variables

Copy `.env.example` from the project root into `backend/.env` and fill in at least one LLM provider API key:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MODAL_API_KEY` | Recommended | — | Modal (GLM-5.1) API key |
| `MODAL_BASE_URL` | No | `https://api.us-west-2.modal.direct/v1` | Modal API base URL |
| `GROQ_API_KEY` | Optional | — | Groq API key |
| `GEMINI_API_KEY` | Optional | — | Google Gemini API key |
| `OLLAMA_ENABLED` | No | `false` | Enable local Ollama provider |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Ollama server URL |
| `DATABASE_URL` | No | `sqlite+aiosqlite:///./data/scripts_writer.db` | Database connection string |
| `EXPORT_DIR` | No | `./data/exports` | Directory for exported files |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Linting & Formatting

```bash
uv run ruff check app/        # Lint
uv run ruff format app/        # Format
uv run ruff check --fix app/   # Auto-fix lint issues
```

## Running Tests

```bash
uv run pytest
```

## Project Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI app, health endpoint, CORS
│   ├── config.py         # AppSettings (pydantic-settings)
│   ├── api/              # REST API routers
│   ├── agents/           # AI agent modules (ICP, Hook, Narrative, etc.)
│   ├── llm/              # LLM provider adapters (Modal, Groq, Gemini, Ollama)
│   ├── pipeline/         # Pipeline orchestrator & state machine
│   ├── services/         # Business logic
│   ├── schemas/          # Pydantic request/response schemas
│   ├── db/               # SQLAlchemy models & migrations
│   └── ws/               # WebSocket handlers
├── tests/
├── scripts/
└── pyproject.toml
```
