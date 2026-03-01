# HashiCorp Vault Secret Management

This directory contains configuration for HashiCorp Vault and External Secrets Operator integration.

## Overview

We use HashiCorp Vault (open source) to securely store secrets, and External Secrets Operator to automatically sync them to Kubernetes.

## Architecture

```
Vault (vault namespace)
  ↓
External Secrets Operator (external-secrets-system namespace)
  ↓
SecretStore (personal-finance namespace)
  ↓
ExternalSecret (personal-finance namespace)
  ↓
Kubernetes Secret (personal-finance namespace)
```

## Components

### 1. Vault Installation
**File**: `vault-values.yaml`

HashiCorp Vault Helm chart values:
- Dev mode enabled for easy setup
- UI enabled at `http://vault.vault.svc.cluster.local:8200`
- KV v2 secrets engine at `secret/`

### 2. Vault Authentication Setup
**File**: `setup-vault-auth.sh`

Configures:
- Kubernetes authentication method
- Service account: `vault-auth`
- Vault policy: `personal-finance-secrets`
- Vault role: `personal-finance`

### 3. SecretStore
**File**: `secret-store.yaml`

Connects External Secrets Operator to Vault:
- Points to Vault server
- Uses Kubernetes auth
- Scoped to `personal-finance` namespace

### 4. ExternalSecret Resources
**File**: `external-secret-postgres.yaml`

Defines which secrets to sync from Vault:
- Source: Vault path `secret/personal-finance/postgres`
- Target: Kubernetes Secret `postgres-secret`
- Refresh interval: 1 minute

## Installation

### Prerequisites
```bash
# Helm 3+ installed
helm version

# kubectl configured
kubectl cluster-info
```

### Install Vault
```bash
# Add Helm repo
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update

# Install Vault
helm install vault hashicorp/vault \
  --namespace vault \
  --create-namespace \
  --values k8s/vault/vault-values.yaml
```

### Install External Secrets Operator
```bash
# Add Helm repo
helm repo add external-secrets https://charts.external-secrets.io
helm repo update

# Install External Secrets
helm install external-secrets \
  external-secrets/external-secrets \
  --namespace external-secrets-system \
  --create-namespace
```

### Configure Vault
```bash
# Run setup script
./k8s/vault/setup-vault-auth.sh

# Store secrets in Vault
kubectl exec -n vault vault-0 -- vault kv put secret/personal-finance/postgres \
  POSTGRES_DB=finance_db \
  POSTGRES_USER=finance_user \
  POSTGRES_PASSWORD=<secure-password> \
  DATABASE_URL="postgresql://finance_user:<secure-password>@postgres:5432/finance_db"
```

### Create SecretStore and ExternalSecret
```bash
# Create SecretStore
kubectl apply -f k8s/vault/secret-store.yaml

# Create ExternalSecret
kubectl apply -f k8s/vault/external-secret-postgres.yaml

# Verify secret was created
kubectl get secret -n personal-finance postgres-secret
```

## Usage

### View Secrets in Vault
```bash
# List all secrets
kubectl exec -n vault vault-0 -- vault kv list secret/personal-finance

# Get specific secret
kubectl exec -n vault vault-0 -- vault kv get secret/personal-finance/postgres
```

### Update Secrets
```bash
# Update in Vault
kubectl exec -n vault vault-0 -- vault kv put secret/personal-finance/postgres \
  POSTGRES_PASSWORD=<new-password> \
  DATABASE_URL="postgresql://finance_user:<new-password>@postgres:5432/finance_db"

# Wait ~1 minute for automatic sync, or force refresh
kubectl annotate externalsecret -n personal-finance postgres-secret-from-vault \
  force-sync=$(date +%s) --overwrite
```

### Troubleshooting

#### Check SecretStore Status
```bash
kubectl get secretstore -n personal-finance vault-backend -o yaml
```

Should show: `status.conditions.type: Ready` with `status: "True"`

#### Check ExternalSecret Status
```bash
kubectl get externalsecret -n personal-finance postgres-secret-from-vault
```

Should show: `STATUS: SecretSynced` and `READY: True`

#### Check Logs
```bash
# External Secrets Operator logs
kubectl logs -n external-secrets-system -l app.kubernetes.io/name=external-secrets

# Vault logs
kubectl logs -n vault vault-0
```

#### Test Vault Authentication
```bash
# Get service account token
SA_TOKEN=$(kubectl get secret -n personal-finance \
  $(kubectl get sa -n personal-finance vault-auth -o jsonpath='{.secrets[0].name}') \
  -o jsonpath='{.data.token}' | base64 -d)

# Login to Vault
kubectl exec -n vault vault-0 -- vault write auth/kubernetes/login \
  role=personal-finance \
  jwt=$SA_TOKEN
```

## Security Considerations

### Dev Mode Warning
⚠️ **Current setup uses Vault in dev mode** - suitable for development/testing only.

For production:
- Disable dev mode
- Enable HA (High Availability)
- Use persistent storage
- Initialize and unseal Vault properly
- Rotate root token
- Enable audit logging

### Access Control
- Vault policies restrict read access to specific paths
- Kubernetes service accounts authenticate via Vault
- RBAC controls who can manage ExternalSecrets

### Rotation
Secrets can be rotated by:
1. Updating value in Vault
2. External Secrets Operator automatically syncs to Kubernetes
3. Pods using the secret will see the new value (may need restart)

## Adding New Secrets

1. **Store in Vault**
```bash
kubectl exec -n vault vault-0 -- vault kv put secret/personal-finance/newsecret \
  KEY1=value1 \
  KEY2=value2
```

2. **Create ExternalSecret**
```yaml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: newsecret-from-vault
  namespace: personal-finance
spec:
  refreshInterval: 1m
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: newsecret
    creationPolicy: Owner
  data:
  - secretKey: KEY1
    remoteRef:
      key: personal-finance/newsecret
      property: KEY1
  - secretKey: KEY2
    remoteRef:
      key: personal-finance/newsecret
      property: KEY2
```

3. **Apply**
```bash
kubectl apply -f newsecret.yaml
```

## Uninstall

```bash
# Remove ExternalSecrets
kubectl delete externalsecret -n personal-finance --all

# Remove SecretStore
kubectl delete secretstore -n personal-finance vault-backend

# Uninstall External Secrets Operator
helm uninstall external-secrets -n external-secrets-system

# Uninstall Vault
helm uninstall vault -n vault

# Delete namespaces (optional)
kubectl delete namespace vault external-secrets-system
```

## References

- [HashiCorp Vault Documentation](https://developer.hashicorp.com/vault/docs)
- [External Secrets Operator](https://external-secrets.io/)
- [Vault Kubernetes Auth](https://developer.hashicorp.com/vault/docs/auth/kubernetes)
