#!/bin/bash

# ==========================================
# Configuration
# ==========================================
BACKEND_DIR="/Users/karpinski94/projects/scripts-writer/backend"
FRONTEND_DIR="/Users/karpinski94/projects/scripts-writer/frontend"

BACKEND_CMD="uv run uvicorn app.main:app --reload"
FRONTEND_CMD="npm run dev"

BACKEND_PORT=8000
FRONTEND_PORT=3000

LOG_DIR="/tmp/scripts-writer-logs"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

mkdir -p "$LOG_DIR"
touch "$BACKEND_LOG"
touch "$FRONTEND_LOG"

# ==========================================
# Helper Functions
# ==========================================

is_running() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null
}

kill_port() {
    local PORT=$1
    local PID=$(lsof -Pi :$PORT -sTCP:LISTEN -t)
    if [ ! -z "$PID" ]; then
        kill -9 $PID >/dev/null 2>&1
    fi
}

# --- BACKGROUND MODE (sw start) ---
start_background() {
    echo "🚀 Starting servers in the background..."

    if ! is_running $BACKEND_PORT; then
        cd "$BACKEND_DIR" && nohup $BACKEND_CMD > "$BACKEND_LOG" 2>&1 &
    fi

    if ! is_running $FRONTEND_PORT; then
        cd "$FRONTEND_DIR" && nohup $FRONTEND_CMD > "$FRONTEND_LOG" 2>&1 &
    fi
    
    echo "✅ Servers started! They are running invisibly."
    echo "ℹ️  Use 'sw logs' to view them, or 'sw stop' to shut them down."
}

# --- FOREGROUND MODE (sw start --logs) ---
start_foreground() {
    echo "🚀 Starting servers in FOREGROUND..."
    
    # Clean up ports first to prevent "Address already in use" errors
    stop_servers >/dev/null

    echo "=========================================="
    echo "🟢 Backend & Frontend logs live below."
    echo "🛑 Press Ctrl+C to stop both servers."
    echo "=========================================="

    # Force colors for terminal outputs
    export FORCE_COLOR=1

    # Start Backend in current terminal
    cd "$BACKEND_DIR" && $BACKEND_CMD &
    BACKEND_PID=$!

    # Start Frontend in current terminal
    cd "$FRONTEND_DIR" && $FRONTEND_CMD &
    FRONTEND_PID=$!

    # TRAP: Catch Ctrl+C and shut them both down cleanly
    trap "echo -e '\n🛑 Ctrl+C detected. Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

    # Keep script running and attached to these processes
    wait $BACKEND_PID $FRONTEND_PID
}

stop_servers() {
    echo "🛑 Stopping servers..."
    kill_port $BACKEND_PORT
    kill_port $FRONTEND_PORT
    echo "✅ All servers stopped."
}

show_logs() {
    echo "=========================================="
    echo "📜 Tailing logs... (Press Ctrl+C to exit logs)"
    echo "=========================================="
    tail -f "$BACKEND_LOG" "$FRONTEND_LOG"
}

# ==========================================
# CLI Routing
# ==========================================

case "$1" in
    start)
        if [ "$2" = "--logs" ]; then
            start_foreground
        else
            start_background
        fi
        ;;
    stop)
        stop_servers
        ;;
    restart)
        stop_servers
        sleep 1
        if [ "$2" = "--logs" ]; then
            start_foreground
        else
            start_background
        fi
        ;;
    logs)
        show_logs
        ;;
    status)
        if is_running $BACKEND_PORT; then echo "🟢 Backend: RUNNING"; else echo "🔴 Backend: STOPPED"; fi
        if is_running $FRONTEND_PORT; then echo "🟢 Frontend: RUNNING"; else echo "🔴 Frontend: STOPPED"; fi
        ;;
    *)
        echo "Usage: sw {start|stop|restart|logs|status} [--logs]"
        exit 1
esac