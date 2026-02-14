#!/bin/bash

set -e

echo "======================================"
echo "Deploying PostgreSQL Database"
echo "======================================"
echo ""

# Check if kubectl is available
command -v kubectl >/dev/null 2>&1 || { echo "ERROR: kubectl not found"; exit 1; }

# Check if minikube is running
minikube status >/dev/null 2>&1 || { echo "ERROR: Minikube is not running"; exit 1; }

echo "Step 1: Creating PostgreSQL resources..."
kubectl apply -f k8s/base/postgres/secret.yaml
kubectl apply -f k8s/base/postgres/configmap.yaml
kubectl apply -f k8s/base/postgres/init-configmap.yaml
kubectl apply -f k8s/base/postgres/pvc.yaml
kubectl apply -f k8s/base/postgres/service.yaml
kubectl apply -f k8s/base/postgres/statefulset.yaml

echo ""
echo "Step 2: Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres --timeout=120s

echo ""
echo "✓ PostgreSQL is running!"
echo ""

# Show PostgreSQL status
echo "PostgreSQL Pod:"
kubectl get pods -l app=postgres

echo ""
echo "PostgreSQL Service:"
kubectl get svc postgres

echo ""
echo "PostgreSQL PVC:"
kubectl get pvc postgres-pvc

echo ""
echo "======================================"
echo "PostgreSQL Deployment Complete!"
echo "======================================"
echo ""
echo "Connection info:"
echo "  Host: postgres (within cluster)"
echo "  Port: 5432"
echo "  Database: finance_db"
echo "  User: finance_user"
echo ""
echo "To run migrations:"
echo "  ./scripts/run-migrations.sh"
echo ""
echo "To connect to database:"
echo "  kubectl exec -it postgres-0 -- psql -U finance_user -d finance_db"
echo ""
