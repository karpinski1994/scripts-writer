#!/bin/bash

# ==========================================
# Configuration
# ==========================================
BACKEND_DIR="/Users/karpinski94/projects/scripts-writer/backend"
FRONTEND_DIR="/Users/karpinski94/projects/scripts-writer/frontend"

BACKEND_CMD="uv run uvicorn app.main:app --reload"
FRONTEND_CMD="npm run dev"

# Change these if your apps use different ports
BACKEND_PORT=8000
FRONTEND_PORT=5173

# Log files to store terminal output
LOG_DIR="/tmp/scripts-writer-logs"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

mkdir -p "$LOG_DIR"

# ==========================================
# Helper Functions
# ==========================================

# Checks if a port is currently in use
is_running() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null
}

# Kills whatever process is running on a specific port
kill_port() {
    local PORT=$1
    local PID=$(lsof -Pi :$PORT -sTCP:LISTEN -t)
    if [ ! -z "$PID" ]; then
        kill -9 $PID
    fi
}

start_servers() {
    echo "🚀 Starting servers..."

    # Start Backend
    if is_running $BACKEND_PORT; then
        echo "✅ Backend is already running on port $BACKEND_PORT."
    else
        echo "⏳ Starting Backend..."
        cd "$BACKEND_DIR" && nohup $BACKEND_CMD > "$BACKEND_LOG" 2>&1 &
        echo "✅ Backend started."
    fi

    # Start Frontend
    if is_running $FRONTEND_PORT; then
        echo "✅ Frontend is already running on port $FRONTEND_PORT."
    else
        echo "⏳ Starting Frontend..."
        cd "$FRONTEND_DIR" && nohup $FRONTEND_CMD > "$FRONTEND_LOG" 2>&1 &
        echo "✅ Frontend started."
    fi
}

stop_servers() {
    echo "🛑 Stopping servers..."
    
    if is_running $BACKEND_PORT; then
        kill_port $BACKEND_PORT
        echo "🛑 Backend stopped."
    else
        echo "⚪️ Backend was not running."
    fi

    if is_running $FRONTEND_PORT; then
        kill_port $FRONTEND_PORT
        echo "🛑 Frontend stopped."
    else
        echo "⚪️ Frontend was not running."
    fi
}

show_logs() {
    echo "📜 Tailing logs... (Press Ctrl+C to exit)"
    tail -f "$BACKEND_LOG" "$FRONTEND_LOG"
}

# ==========================================
# CLI Routing
# ==========================================

case "$1" in
    start)
        start_servers
        ;;
    stop)
        stop_servers
        ;;
    restart)
        stop_servers
        sleep 1
        start_servers
        ;;
    logs)
        show_logs
        ;;
    status)
        if is_running $BACKEND_PORT; then echo "🟢 Backend: RUNNING"; else echo "🔴 Backend: STOPPED"; fi
        if is_running $FRONTEND_PORT; then echo "🟢 Frontend: RUNNING"; else echo "🔴 Frontend: STOPPED"; fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|status}"
        exit 1
esac