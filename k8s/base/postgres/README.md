# PostgreSQL Kubernetes Resources

This directory contains Kubernetes manifests for deploying PostgreSQL database.

## Files

- `configmap.yaml` - PostgreSQL configuration settings
- `init-configmap.yaml` - Initialization scripts
- `pvc.yaml` - Persistent Volume Claim for database storage (10Gi)
- `service.yaml` - Headless service for StatefulSet
- `statefulset.yaml` - PostgreSQL StatefulSet deployment
- `migration-job.yaml` - Kubernetes Job to run database migrations
- `secret.yaml.template` - Template for database credentials (copy to secret.yaml)

## Setup

### 1. Create Secret

Copy the template and customize credentials:

```bash
cd k8s/base/postgres
cp secret.yaml.template secret.yaml
# Edit secret.yaml with your own credentials
```

**Important:** Never commit `secret.yaml` to version control. It's ignored by .gitignore.

For development, you can use the default credentials in the template.

### 2. Deploy PostgreSQL

Use the automated script:

```bash
./scripts/deploy-database.sh
```

Or deploy manually:

```bash
kubectl apply -f k8s/base/postgres/secret.yaml
kubectl apply -f k8s/base/postgres/configmap.yaml
kubectl apply -f k8s/base/postgres/init-configmap.yaml
kubectl apply -f k8s/base/postgres/pvc.yaml
kubectl apply -f k8s/base/postgres/service.yaml
kubectl apply -f k8s/base/postgres/statefulset.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres --timeout=120s
```

### 3. Run Migrations

Use the automated script:

```bash
./scripts/run-migrations.sh
```

Or using Makefile:

```bash
make run-migrations
```

## Accessing the Database

### From within the cluster

Services can connect using:
- Host: `postgres`
- Port: `5432`
- Database: `finance_db`
- User: `finance_user`
- Password: (from secret)

### From your local machine

Use kubectl port-forward:

```bash
kubectl port-forward svc/postgres 5432:5432
psql -h localhost -U finance_user -d finance_db
```

### Direct pod access

```bash
kubectl exec -it postgres-0 -- psql -U finance_user -d finance_db
```

## Database Schema

The database contains the following tables:

- `accounts` - Financial accounts (checking, savings, credit cards, etc.)
- `transactions` - Individual transactions
- `categories` - Transaction categories (hierarchical)
- `budgets` - Budget allocations
- `import_logs` - CSV import history
- `holdings` - Investment holdings (for brokerage accounts)
- `csv_mapping_rules` - CSV column mapping rules by institution

## Migrations

Migrations are managed using a custom migration system:

- Migration files are located in `database/migrations/`
- File naming: `V###__description.sql` (e.g., `V001__initial_schema.sql`)
- Migrations are tracked in the `schema_migrations` table
- Migrations are applied in order and only run once

## Seed Data

Default categories are populated from `database/seeds/001_default_categories.sql`:

- 14 parent categories (Income, Housing, Utilities, Transportation, etc.)
- 73 subcategories
- Total: 87 categories

## Backup and Restore

### Backup

```bash
kubectl exec postgres-0 -- pg_dump -U finance_user finance_db > backup.sql
```

### Restore

```bash
kubectl exec -i postgres-0 -- psql -U finance_user -d finance_db < backup.sql
```

## Troubleshooting

### Pod not starting

```bash
# Check pod status
kubectl describe pod postgres-0

# Check logs
kubectl logs postgres-0
```

### PVC not binding

```bash
# Check PVC status
kubectl get pvc postgres-pvc
kubectl describe pvc postgres-pvc

# Check if PV is available
kubectl get pv
```

### Connection issues

```bash
# Test connection from pod
kubectl exec postgres-0 -- pg_isready -U finance_user

# Check service
kubectl get svc postgres

# Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup postgres
```

### Reset database

To completely reset the database:

```bash
kubectl delete statefulset postgres
kubectl delete pvc postgres-pvc
kubectl apply -f k8s/base/postgres/
```

## Security Notes

- **Development Only**: Default credentials are for development use only
- **Production**: Use strong passwords and consider:
  - External secrets management (Vault, Sealed Secrets)
  - Database encryption at rest
  - Network policies to restrict access
  - Regular backups with encryption
  - Monitoring and audit logging

## Resource Limits

Current configuration:

- Memory: 256Mi - 1Gi
- CPU: 250m - 1000m
- Storage: 10Gi

Adjust in `statefulset.yaml` based on your needs.
