# PostgreSQL Secrets

## ⚠️ IMPORTANT: Secrets are managed by HashiCorp Vault

This directory previously contained a plaintext `secret.yaml` file. For security reasons, secrets are now managed through **HashiCorp Vault** and **External Secrets Operator**.

## How Secrets Work

1. **Secrets are stored in Vault** at path: `secret/personal-finance/postgres`
2. **External Secrets Operator** syncs secrets from Vault to Kubernetes
3. **Kubernetes Secret** (`postgres-secret`) is automatically created and kept in sync

## Accessing/Updating Secrets

### View Current Secrets (from Vault)
```bash
kubectl exec -n vault vault-0 -- vault kv get secret/personal-finance/postgres
```

### Update Secrets in Vault
```bash
kubectl exec -n vault vault-0 -- vault kv put secret/personal-finance/postgres \
  POSTGRES_DB=finance_db \
  POSTGRES_USER=finance_user \
  POSTGRES_PASSWORD=<new-password> \
  DATABASE_URL="postgresql://finance_user:<new-password>@postgres:5432/finance_db"
```

The External Secrets Operator will automatically sync the updated values to Kubernetes within 1 minute.

### Verify Secret in Kubernetes
```bash
kubectl get secret -n personal-finance postgres-secret -o yaml
```

## For Developers

If you need to set up secrets for local development:

1. Ensure Vault is running and initialized
2. Store secrets in Vault (see commands above)
3. The ExternalSecret resource will automatically create the Kubernetes secret

**Never commit plaintext secrets to Git!**

## Architecture

```
┌─────────────────┐
│  HashiCorp      │
│  Vault          │◄─── Secrets stored here
│  (vault ns)     │
└────────┬────────┘
         │
         │ Vault API
         │
┌────────▼────────────────┐
│  External Secrets       │
│  Operator               │
│  (external-secrets-     │
│   system ns)            │
└────────┬────────────────┘
         │
         │ Creates/Updates
         │
┌────────▼────────────────┐
│  Kubernetes Secret      │
│  postgres-secret        │
│  (personal-finance ns)  │
└─────────────────────────┘
         │
         │ Consumed by
         │
    ┌────▼─────┐
    │PostgreSQL│
    │ETL       │
    │etc.      │
    └──────────┘
```

## Benefits

- ✅ **No plaintext secrets in Git** - improved security
- ✅ **Centralized secret management** - all secrets in Vault
- ✅ **Automatic rotation** - update in Vault, syncs to K8s
- ✅ **Audit trail** - Vault logs all secret access
- ✅ **Access control** - Vault policies control who can read/write
