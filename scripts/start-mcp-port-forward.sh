#!/bin/bash
# Start port-forward for MCP server in Kubernetes

echo "Starting MCP server port-forward..."
echo "  Kubernetes service: mcp-server"
echo "  Local port: 8082"
echo "  Remote port: 8081"
echo ""

# Kill existing port-forward
pkill -f "kubectl port-forward svc/mcp-server" 2>/dev/null || true

# Start port-forward in background
kubectl port-forward svc/mcp-server 8082:8081 -n default > /tmp/mcp-port-forward.log 2>&1 &
PID=$!

# Wait for port-forward to be ready
sleep 2

# Check if it's working
if lsof -i:8082 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✓ MCP server port-forward active (PID: $PID)"
    echo "✓ Accessible at: http://localhost:8082"
    echo "✓ SSE endpoint: http://localhost:8082/sse"
    echo ""
    echo "Health check:"
    curl -s http://localhost:8082/health | jq
    echo ""
    echo "To stop: pkill -f 'kubectl port-forward svc/mcp-server'"
else
    echo "✗ Failed to start port-forward"
    exit 1
fi
