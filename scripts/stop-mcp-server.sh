#!/bin/bash
# Stop the Personal Finance MCP Server and related port-forwards

echo "=== Stopping Personal Finance MCP Server ==="

# Kill MCP server processes
MCP_PIDS=$(pgrep -f "python.*main.py" || true)
if [ -n "$MCP_PIDS" ]; then
    echo "Stopping MCP server processes..."
    echo "$MCP_PIDS" | xargs kill -9 2>/dev/null || true
    echo "✓ MCP server stopped"
else
    echo "No MCP server processes found"
fi

# Kill PostgreSQL port-forward
POSTGRES_PF_PIDS=$(lsof -ti:5432 2>/dev/null || true)
if [ -n "$POSTGRES_PF_PIDS" ]; then
    echo "Stopping PostgreSQL port-forward..."
    echo "$POSTGRES_PF_PIDS" | xargs kill 2>/dev/null || true
    echo "✓ PostgreSQL port-forward stopped"
else
    echo "No PostgreSQL port-forward found"
fi

# Kill MCP server port if occupied
MCP_PORT_PIDS=$(lsof -ti:8081 2>/dev/null || true)
if [ -n "$MCP_PORT_PIDS" ]; then
    echo "Stopping processes on port 8081..."
    echo "$MCP_PORT_PIDS" | xargs kill 2>/dev/null || true
    echo "✓ Port 8081 freed"
fi

echo "✓ Cleanup complete"
