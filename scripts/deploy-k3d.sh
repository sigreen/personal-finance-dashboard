#!/bin/bash

set -e

echo "======================================"
echo "Deploying to k3d"
echo "======================================"
echo ""

# Check kubectl is available
command -v kubectl >/dev/null 2>&1 || { echo "ERROR: kubectl is not installed."; exit 1; }

# Apply namespace and base resources using kustomize
echo "Applying base resources with kustomize..."
kubectl apply -k k8s/overlays/personal-finance/
echo "✓ Base resources applied"
echo ""

# Wait for postgres to be ready
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n personal-finance --timeout=180s || true
echo ""

# Run database migrations
echo "Running database migrations..."
kubectl apply -f k8s/base/postgres/migration-job.yaml -n personal-finance
echo "Waiting for migration job to complete..."
kubectl wait --for=condition=complete job/db-migration -n personal-finance --timeout=120s || true
echo "✓ Database migrations complete"
echo ""

# Apply Gateway API resources
echo "Applying Gateway API resources..."
kubectl apply -f k8s/gateway/
echo "✓ Gateway API resources applied"
echo ""

# Apply Kagenti MCP registration
echo "Applying Kagenti MCP registration..."
kubectl apply -f k8s/kagenti/
echo "✓ Kagenti MCP registration applied"
echo ""

# Wait for deployments to be ready
echo "Waiting for deployments to be ready..."
kubectl rollout status deployment/frontend -n personal-finance --timeout=120s || true
kubectl rollout status deployment/etl-service -n personal-finance --timeout=120s || true
kubectl rollout status deployment/mcp-server -n personal-finance --timeout=120s || true
kubectl rollout status statefulset/postgres -n personal-finance --timeout=120s || true
echo ""

echo "======================================"
echo "Deployment Status"
echo "======================================"
kubectl get pods -n personal-finance
echo ""
kubectl get svc -n personal-finance
echo ""
kubectl get gateway -n personal-finance
echo ""
kubectl get httproute -n personal-finance
echo ""

echo "======================================"
echo "✓ Deployment Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Get the Gateway IP:"
echo "   kubectl get gateway personal-finance-gateway -n personal-finance -o jsonpath='{.status.addresses[0].value}'"
echo ""
echo "2. Add to /etc/hosts:"
echo "   <GATEWAY_IP>  finance.local"
echo ""
echo "3. Access services:"
echo "   Frontend: http://finance.local/"
echo "   MCP Server: http://finance.local/mcp/sse"
echo ""
