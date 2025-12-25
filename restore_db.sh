#!/bin/bash
# Restore PostgreSQL database from backup

if [ -z "$1" ]; then
    echo "Usage: ./restore_db.sh <backup_file.sql.gz>"
    echo ""
    echo "Available backups:"
    ls -lh ./backups/*.gz 2>/dev/null || echo "  No backups found"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "✗ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  WARNING: This will overwrite the current database!"
echo "Backup file: $BACKUP_FILE"
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

echo "Stopping backend and worker containers..."
docker-compose stop backend celery-worker

echo "Decompressing backup..."
TEMP_SQL="/tmp/restore_temp.sql"
gunzip -c "$BACKUP_FILE" > "$TEMP_SQL"

echo "Dropping existing database..."
docker-compose exec -T postgres psql -U lead_gen_user -d postgres -c "DROP DATABASE IF EXISTS lead_gen_db;"

echo "Creating fresh database..."
docker-compose exec -T postgres psql -U lead_gen_user -d postgres -c "CREATE DATABASE lead_gen_db;"

echo "Restoring from backup..."
docker-compose exec -T postgres psql -U lead_gen_user -d lead_gen_db < "$TEMP_SQL"

if [ $? -eq 0 ]; then
    echo "✓ Restore successful"
    rm "$TEMP_SQL"
    
    echo "Starting backend and worker containers..."
    docker-compose start backend celery-worker
    
    echo "✓ Database restored and services restarted"
    exit 0
else
    echo "✗ Restore failed"
    rm "$TEMP_SQL"
    exit 1
fi
