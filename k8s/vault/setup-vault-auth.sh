#!/bin/bash
# Configure Vault for Kubernetes authentication and External Secrets

set -e

echo "========================================="
echo "Configuring Vault Authentication"
echo "========================================="
echo ""

# Create service account for External Secrets
echo "Creating service account for External Secrets..."
kubectl create serviceaccount vault-auth -n personal-finance 2>/dev/null || echo "Service account already exists"

# Enable Kubernetes auth in Vault
echo "Enabling Kubernetes auth method in Vault..."
kubectl exec -n vault vault-0 -- vault auth enable kubernetes 2>/dev/null || echo "Kubernetes auth already enabled"

# Configure Kubernetes auth
echo "Configuring Kubernetes auth..."
kubectl exec -n vault vault-0 -- vault write auth/kubernetes/config \
  kubernetes_host="https://kubernetes.default.svc:443"

# Create Vault policy for reading secrets
echo "Creating Vault policy..."
kubectl exec -n vault vault-0 -- vault policy write personal-finance-secrets - <<EOF
path "secret/data/personal-finance/*" {
  capabilities = ["read", "list"]
}
EOF

# Create Vault role for the service account
echo "Creating Vault role..."
kubectl exec -n vault vault-0 -- vault write auth/kubernetes/role/personal-finance \
  bound_service_account_names=vault-auth \
  bound_service_account_namespaces=personal-finance \
  policies=personal-finance-secrets \
  ttl=24h

echo ""
echo "========================================="
echo "Vault Authentication Configured"
echo "========================================="
echo ""
echo "Service Account: vault-auth"
echo "Namespace: personal-finance"
echo "Policy: personal-finance-secrets"
echo "Role: personal-finance"
echo ""
