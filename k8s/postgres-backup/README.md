# PostgreSQL Backup and High Availability

This directory contains backup and HA configurations for the personal-finance PostgreSQL database.

## Backup Solution

### Features
- **Automated daily backups** at 2 AM
- **30-day retention policy** - automatically cleans up old backups
- **Compressed backups** using PostgreSQL custom format with maximum compression
- **20GB dedicated storage** for backups
- **Verification** - ensures backup files are created and not empty

### Deployment

Deploy the backup solution:
```bash
kubectl apply -f personal-finance-backup.yaml
```

### Verify Backup CronJob

Check if the CronJob is created:
```bash
kubectl get cronjob -n personal-finance postgres-backup
```

### Manual Backup

Trigger a manual backup immediately:
```bash
kubectl create job -n personal-finance --from=cronjob/postgres-backup manual-backup-$(date +%s)
```

Watch the backup job:
```bash
kubectl logs -n personal-finance -l app=postgres-backup --follow
```

### List Available Backups

```bash
kubectl run -n personal-finance backup-list --image=postgres:15-alpine --rm -it --restart=Never \
  --overrides='
{
  "spec": {
    "containers": [{
      "name": "backup-list",
      "image": "postgres:15-alpine",
      "command": ["ls", "-lh", "/backups"],
      "volumeMounts": [{
        "name": "backup-storage",
        "mountPath": "/backups"
      }]
    }],
    "volumes": [{
      "name": "backup-storage",
      "persistentVolumeClaim": {
        "claimName": "postgres-backup-storage"
      }
    }]
  }
}' -- ls -lh /backups
```

## Restore Solution

### Restore from Backup

1. **Find the backup you want to restore:**
   ```bash
   # List backups (see command above)
   ```

2. **Edit the restore job** to specify the backup file:
   ```bash
   # Edit restore-job.yaml and update RESTORE_FILE variable
   # Example: RESTORE_FILE=finance_db_20260301_020000.dump
   ```

3. **Scale down applications** to prevent conflicts:
   ```bash
   kubectl scale deployment -n personal-finance etl-service frontend --replicas=0
   ```

4. **Run the restore job:**
   ```bash
   kubectl apply -f restore-job.yaml
   ```

5. **Monitor the restore:**
   ```bash
   kubectl logs -n personal-finance -l app=postgres-restore --follow
   ```

6. **Scale applications back up:**
   ```bash
   kubectl scale deployment -n personal-finance etl-service frontend --replicas=1
   ```

### Quick Restore Script

For convenience, use this one-liner (update the backup filename):
```bash
BACKUP_FILE="finance_db_20260301_020000.dump" && \
kubectl scale deployment -n personal-finance etl-service frontend --replicas=0 && \
cat restore-job.yaml | sed "s/finance_db_YYYYMMDD_HHMMSS.dump/${BACKUP_FILE}/" | kubectl apply -f - && \
kubectl wait --for=condition=complete --timeout=600s job/postgres-restore -n personal-finance && \
kubectl scale deployment -n personal-finance etl-service frontend --replicas=1
```

## High Availability (HA)

For production HA, we recommend using a PostgreSQL operator. Here are the options:

### Option 1: CloudNativePG (Recommended)
```bash
# Install the operator
kubectl apply -f https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.22/releases/cnpg-1.22.0.yaml

# Then create a cluster with:
# - 3 replicas for HA
# - Automatic failover
# - Integrated backup
# - Connection pooling
```

### Option 2: Crunchy Data PGO
```bash
# Provides enterprise-grade PostgreSQL with:
# - HA with automatic failover
# - Point-in-time recovery
# - Monitoring and observability
```

### Option 3: Zalando Postgres Operator
```bash
# Lightweight operator with:
# - Master-replica setup
# - Automatic failover via Patroni
# - Connection pooling
```

## Current Status

- ✅ Automated daily backups
- ✅ 30-day retention
- ✅ Manual backup capability
- ✅ Restore procedure
- ⏳ HA (pending operator deployment)

## Monitoring

### Check Last Backup
```bash
kubectl get jobs -n personal-finance -l app=postgres-backup --sort-by=.status.startTime
```

### View Backup Logs
```bash
kubectl logs -n personal-finance -l app=postgres-backup --tail=100
```

### Check Backup Storage Usage
```bash
kubectl exec -n personal-finance postgres-0 -- df -h /backups
```

## Backup File Format

Backups are in PostgreSQL custom format (`.dump`):
- **Compressed** with gzip level 9
- **Portable** across PostgreSQL versions
- **Selective restore** - can restore specific tables/schemas
- **Parallel restore** - faster restore on multi-core systems

## Security Notes

- Backup credentials are read from existing `postgres-secret`
- Backup jobs run as non-root user (UID 999)
- Backups are stored encrypted-at-rest by the storage backend
- Consider encrypting backups before offsite storage

## Disaster Recovery

For offsite backups, sync to external storage:
```bash
# Example: Sync to S3, Azure Blob, or Google Cloud Storage
kubectl create job -n personal-finance sync-backups --image=rclone/rclone -- \
  rclone sync /backups remote:postgres-backups
```
