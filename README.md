# Scripts Writer

A full-stack application for generating video scripts and marketing posts using AI agents.

## Project Structure

- `backend/` — FastAPI backend with AI agent pipeline
- `frontend/` — Next.js frontend
- `dev.sh` — Development helper script

## Quick Start

### 1. Install Dependencies

**Backend:**
```bash
cd backend
cp ../.env.example .env
# Edit .env with your API keys
uv sync
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Run the Application

Use the provided `dev.sh` script:

```bash
# Start both servers
./dev.sh start

# Stop both servers
./dev.sh stop

# Restart both servers
./dev.sh restart

# View logs
./dev.sh logs

# Check status
./dev.sh status
```

The backend runs on **http://localhost:8000** (API docs at `/docs`) and the frontend on **http://localhost:5173** (or 5173, check the output).

---

## Setting Up dev.sh on Different Machines

The script is configured for a specific machine by default. To use it on a different machine:

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd scripts-writer
```

### 2. Configure the Script Paths

Open `dev.sh` and edit the `BACKEND_DIR` and `FRONTEND_DIR` variables at the top:

```bash
BACKEND_DIR="/path/to/your/scripts-writer/backend"
FRONTEND_DIR="/path/to/your/scripts-writer/frontend"
```

Update these to point to the actual locations on your machine.

### 3. Ensure Executable Permission

```bash
chmod +x dev.sh
```

### 4. Adjust Ports if Needed

If ports 8000 or 5173 are already in use on your machine, change them in the script:

```bash
BACKEND_PORT=8000    # Change if needed
FRONTEND_PORT=5173   # Change if needed
```

### 5. Run Prerequisites

- **Backend**: Install Python 3.11+, uv, and run `uv sync` in the backend directory
- **Frontend**: Install Node.js and run `npm install` in the frontend directory

### 6. Start Development

```bash
./dev.sh start
```

---

## Environment Setup

Copy `.env.example` to `.env` in the backend directory and configure at least one LLM provider:

- `MODEL_API_KEY` — Required for at least one provider (Modal, Groq, Gemini, or Ollama)

See `backend/README.md` for full environment variable documentation.

---

## Available Commands

| Command | Description |
|---------|-------------|
| `./dev.sh start` | Start servers in background (invisible) |
| `./dev.sh start --logs` | Start servers in foreground with live logs (Ctrl+C to stop) |
| `./dev.sh stop` | Stop both servers |
| `./dev.sh restart` | Restart servers in background |
| `./dev.sh restart --logs` | Restart servers in foreground |
| `./dev.sh logs` | Tail server logs |
| `./dev.sh status` | Check if servers are running |

### Usage Modes

**Background Mode (default):**
```bash
./dev.sh start
```
Servers start silently in the background. Use `./dev.sh logs` to view output or `./dev.sh stop` to shut them down.

**Foreground Mode (interactive):**
```bash
./dev.sh start --logs
```
Both servers boot inside your terminal with full color output. Press `Ctrl+C` to stop both servers cleanly.