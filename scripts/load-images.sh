#!/bin/bash

set -e

echo "======================================"
echo "Loading Images into Minikube"
echo "======================================"
echo ""

# Check if minikube is running
minikube status >/dev/null 2>&1 || { echo "ERROR: Minikube is not running. Start it with 'minikube start'"; exit 1; }

# Load ETL Service
if podman images | grep -q finance-etl; then
    echo "Loading ETL service image..."
    minikube image load finance-etl:latest
    echo "✓ ETL service image loaded"
    echo ""
else
    echo "⚠ Skipping ETL service (image not found)"
    echo ""
fi

# Load MCP Server
if podman images | grep -q finance-mcp; then
    echo "Loading MCP server image..."
    minikube image load finance-mcp:latest
    echo "✓ MCP server image loaded"
    echo ""
else
    echo "⚠ Skipping MCP server (image not found)"
    echo ""
fi

# Load Frontend
if podman images | grep -q finance-frontend; then
    echo "Loading frontend image..."
    minikube image load finance-frontend:latest
    echo "✓ Frontend image loaded"
    echo ""
else
    echo "⚠ Skipping frontend (image not found)"
    echo ""
fi

echo "======================================"
echo "Images in Minikube:"
echo "======================================"
minikube image ls | grep finance || echo "No finance images found in minikube"
echo ""
