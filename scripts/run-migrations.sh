#!/bin/bash

set -e

echo "======================================"
echo "Running Database Migrations"
echo "======================================"
echo ""

# Check if Podman is available
command -v podman >/dev/null 2>&1 || { echo "ERROR: Podman not found"; exit 1; }

# Check if kubectl is available
command -v kubectl >/dev/null 2>&1 || { echo "ERROR: kubectl not found"; exit 1; }

# Check if PostgreSQL is running
kubectl get pod postgres-0 >/dev/null 2>&1 || { echo "ERROR: PostgreSQL pod not found. Deploy database first."; exit 1; }

echo "Step 1: Building migration container..."
podman build -t finance-db-migration:latest -f database/Containerfile database/

echo ""
echo "Step 2: Loading image into minikube..."
podman save localhost/finance-db-migration:latest -o /tmp/finance-db-migration.tar
minikube image load /tmp/finance-db-migration.tar
rm /tmp/finance-db-migration.tar

echo ""
echo "Step 3: Deleting any existing migration job..."
kubectl delete job postgres-migration 2>/dev/null || true

echo ""
echo "Step 4: Running migration job..."
kubectl apply -f k8s/base/postgres/migration-job.yaml

echo ""
echo "Step 5: Waiting for migration to complete..."
kubectl wait --for=condition=complete job/postgres-migration --timeout=120s

echo ""
echo "======================================"
echo "Migration Logs:"
echo "======================================"
kubectl logs job/postgres-migration

echo ""
echo "======================================"
echo "✓ Migrations completed successfully!"
echo "======================================"
echo ""
echo "To verify the database schema:"
echo "  kubectl exec -it postgres-0 -- psql -U finance_user -d finance_db -c '\\dt'"
echo ""
