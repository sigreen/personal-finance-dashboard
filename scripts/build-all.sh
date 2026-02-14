#!/bin/bash

set -e

echo "======================================"
echo "Building All Container Images"
echo "======================================"
echo ""

# Check if Podman is installed
command -v podman >/dev/null 2>&1 || { echo "ERROR: Podman is not installed."; exit 1; }

# Build ETL Service
if [ -f backend/etl-service/Containerfile ]; then
    echo "Building ETL service image..."
    podman build -t finance-etl:latest ./backend/etl-service
    echo "✓ ETL service image built"
    echo ""
else
    echo "⚠ Skipping ETL service (Containerfile not found)"
    echo ""
fi

# Build MCP Server
if [ -f backend/mcp-server/Containerfile ]; then
    echo "Building MCP server image..."
    podman build -t finance-mcp:latest ./backend/mcp-server
    echo "✓ MCP server image built"
    echo ""
else
    echo "⚠ Skipping MCP server (Containerfile not found)"
    echo ""
fi

# Build Frontend
if [ -f frontend/Containerfile ]; then
    echo "Building frontend image..."
    podman build -t finance-frontend:latest ./frontend
    echo "✓ Frontend image built"
    echo ""
else
    echo "⚠ Skipping frontend (Containerfile not found)"
    echo ""
fi

echo "======================================"
echo "Built Images:"
echo "======================================"
podman images | grep finance || echo "No finance images found"
echo ""

echo "To load images into minikube, run:"
echo "  ./scripts/load-images.sh"
echo ""
