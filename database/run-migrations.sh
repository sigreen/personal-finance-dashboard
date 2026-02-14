#!/bin/bash
set -e

echo "======================================"
echo "Database Migration Script"
echo "======================================"
echo ""

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "✓ PostgreSQL is ready"
echo ""

# Check if migrations table exists
echo "Checking for migrations table..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<-EOSQL
  CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT
  );
EOSQL

echo "✓ Migrations table ready"
echo ""

# Run migrations in order
echo "Applying migrations..."
for migration in /migrations/V*.sql; do
  if [ -f "$migration" ]; then
    # Extract version from filename (e.g., V001__initial_schema.sql -> V001)
    filename=$(basename "$migration")
    version=$(echo "$filename" | cut -d'_' -f1)
    description=$(echo "$filename" | sed 's/^V[0-9]*__//; s/.sql$//' | tr '_' ' ')

    # Check if migration has already been applied
    already_applied=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM schema_migrations WHERE version='$version';")

    if [ "$already_applied" -eq 0 ]; then
      echo "Applying migration: $filename"
      PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$migration"

      # Record migration
      PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<-EOSQL
        INSERT INTO schema_migrations (version, description) VALUES ('$version', '$description');
EOSQL
      echo "✓ Migration $version applied successfully"
    else
      echo "⊘ Migration $version already applied, skipping"
    fi
  fi
done

echo ""
echo "======================================"
echo "Running Seed Data..."
echo "======================================"
echo ""

# Run seed data
for seed in /seeds/*.sql; do
  if [ -f "$seed" ]; then
    filename=$(basename "$seed")
    echo "Applying seed data: $filename"

    # Check if seed has already been applied (based on category count as a heuristic)
    category_count=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM categories;")

    if [ "$category_count" -eq 0 ]; then
      PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$seed"
      echo "✓ Seed data applied successfully"
    else
      echo "⊘ Seed data already exists, skipping"
    fi
  fi
done

echo ""
echo "======================================"
echo "Migration Summary"
echo "======================================"
echo ""

# Show applied migrations
echo "Applied migrations:"
PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT version, description, applied_at FROM schema_migrations ORDER BY version;"

echo ""
echo "Database schema:"
PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\dt"

echo ""
echo "✓ All migrations completed successfully!"
