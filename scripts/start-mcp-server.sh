#!/bin/bash
# Start the Personal Finance MCP Server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MCP_SERVER_DIR="$PROJECT_ROOT/backend/mcp-server"

echo "=== Starting Personal Finance MCP Server ==="

# Check if PostgreSQL port-forward is running
if ! lsof -i:5432 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  PostgreSQL port-forward not detected on port 5432"
    echo "Starting port-forward in background..."

    # Start port-forward in background
    kubectl port-forward svc/postgres 5432:5432 -n default > /tmp/postgres-port-forward.log 2>&1 &
    PORTFWD_PID=$!
    echo "Port-forward started (PID: $PORTFWD_PID)"

    # Wait for port-forward to be ready
    echo -n "Waiting for port-forward to be ready"
    for i in {1..10}; do
        if lsof -i:5432 -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo " ✓"
            break
        fi
        echo -n "."
        sleep 1
    done

    if ! lsof -i:5432 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo " ✗"
        echo "Failed to establish port-forward. Check kubectl access."
        exit 1
    fi
else
    echo "✓ PostgreSQL port-forward detected on port 5432"
fi

# Navigate to MCP server directory
cd "$MCP_SERVER_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found, using .env.example"
    cp .env.example .env
fi

# Run the server
echo ""
echo "=========================================="
echo "Starting MCP Server..."
echo "=========================================="
echo "SSE Endpoint: http://127.0.0.1:8081/sse"
echo "Health Check: http://127.0.0.1:8081/health"
echo "=========================================="
echo ""

python main.py
