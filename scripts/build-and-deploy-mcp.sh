#!/bin/bash
# Build and deploy MCP server to Kubernetes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MCP_DIR="$PROJECT_ROOT/backend/mcp-server"

echo "=== Building and Deploying MCP Server to Kubernetes ==="

# Stop local MCP server if running
echo ""
echo "1. Stopping local MCP server..."
pkill -f "python.*main.py" 2>/dev/null || echo "   No local server running"

# Build container image
echo ""
echo "2. Building container image..."
cd "$MCP_DIR"
podman build -t finance-mcp:latest -f Containerfile .

# Load image into minikube
echo ""
echo "3. Loading image into minikube..."
minikube image load finance-mcp:latest

# Deploy to Kubernetes
echo ""
echo "4. Deploying to Kubernetes..."
kubectl apply -f "$PROJECT_ROOT/k8s/base/mcp-server-deployment.yaml"

# Wait for deployment
echo ""
echo "5. Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=60s deployment/mcp-server

# Get service info
echo ""
echo "6. Getting service information..."
kubectl get svc mcp-server

# Get LoadBalancer IP
echo ""
echo "7. Waiting for LoadBalancer IP..."
for i in {1..30}; do
    EXTERNAL_IP=$(kubectl get svc mcp-server -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    if [ -n "$EXTERNAL_IP" ]; then
        echo "   ✓ LoadBalancer IP: $EXTERNAL_IP"
        break
    fi
    echo -n "."
    sleep 2
done

if [ -z "$EXTERNAL_IP" ]; then
    echo ""
    echo "   ⚠️  LoadBalancer IP not assigned yet"
    echo "   You can check later with: kubectl get svc mcp-server"
else
    echo ""
    echo "=== Deployment Complete! ==="
    echo ""
    echo "MCP Server is now running in Kubernetes"
    echo "Access via: http://$EXTERNAL_IP:8081"
    echo "SSE endpoint: http://$EXTERNAL_IP:8081/sse"
    echo "Health check: http://$EXTERNAL_IP:8081/health"
    echo ""
    echo "Update your .mcp.json with:"
    echo "{"
    echo "  \"mcpServers\": {"
    echo "    \"personal-finance\": {"
    echo "      \"url\": \"http://$EXTERNAL_IP:8081/sse\","
    echo "      \"type\": \"sse\""
    echo "    }"
    echo "  }"
    echo "}"
    echo ""
    echo "To test:"
    echo "  curl http://$EXTERNAL_IP:8081/health"
fi

echo ""
echo "Useful commands:"
echo "  kubectl get pods -l app=mcp-server          # Check pod status"
echo "  kubectl logs -f -l app=mcp-server           # View logs"
echo "  kubectl get svc mcp-server                  # Get service info"
echo "  kubectl delete -f k8s/base/mcp-server-deployment.yaml  # Remove deployment"
