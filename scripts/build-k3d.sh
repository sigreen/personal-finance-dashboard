#!/bin/bash

set -e

echo "======================================"
echo "Building Images for k3d"
echo "======================================"
echo ""

# Check if Podman is installed
command -v podman >/dev/null 2>&1 || { echo "ERROR: Podman is not installed."; exit 1; }
command -v k3d >/dev/null 2>&1 || { echo "ERROR: k3d is not installed."; exit 1; }

# Set cluster name
CLUSTER_NAME="${K3D_CLUSTER:-kagenti}"

# Registry endpoint (not used for import, but set for future use)
REGISTRY="localhost:5555"

echo "Building and importing images for cluster: $CLUSTER_NAME"
echo ""

# Build ETL Service
if [ -f backend/etl-service/Containerfile ]; then
    echo "Building ETL service image..."
    podman build -t ${REGISTRY}/finance-etl:latest ./backend/etl-service
    echo "✓ ETL service image built"
    echo "Saving and importing ETL image into k3d..."
    podman save ${REGISTRY}/finance-etl:latest -o /tmp/finance-etl.tar
    k3d image import /tmp/finance-etl.tar -c $CLUSTER_NAME
    rm /tmp/finance-etl.tar
    echo "✓ ETL service image imported"
    echo ""
else
    echo "⚠ Skipping ETL service (Containerfile not found)"
    echo ""
fi

# Build MCP Server
if [ -f backend/mcp-server/Containerfile ]; then
    echo "Building MCP server image..."
    podman build -t ${REGISTRY}/finance-mcp:latest ./backend/mcp-server
    echo "✓ MCP server image built"
    echo "Saving and importing MCP server image into k3d..."
    podman save ${REGISTRY}/finance-mcp:latest -o /tmp/finance-mcp.tar
    k3d image import /tmp/finance-mcp.tar -c $CLUSTER_NAME
    rm /tmp/finance-mcp.tar
    echo "✓ MCP server image imported"
    echo ""
else
    echo "⚠ Skipping MCP server (Containerfile not found)"
    echo ""
fi

# Build Frontend
if [ -f frontend/Containerfile ]; then
    echo "Building frontend image..."
    podman build -t ${REGISTRY}/finance-frontend:latest ./frontend
    echo "✓ Frontend image built"
    echo "Saving and importing frontend image into k3d..."
    podman save ${REGISTRY}/finance-frontend:latest -o /tmp/finance-frontend.tar
    k3d image import /tmp/finance-frontend.tar -c $CLUSTER_NAME
    rm /tmp/finance-frontend.tar
    echo "✓ Frontend image imported"
    echo ""
else
    echo "⚠ Skipping frontend (Containerfile not found)"
    echo ""
fi

echo "======================================"
echo "Images in k3d cluster:"
echo "======================================"
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | while read node; do
    echo "Node: $node"
    docker exec $node crictl images | grep finance || echo "  No finance images found"
done
echo ""

echo "✓ Build and import complete!"
echo ""
