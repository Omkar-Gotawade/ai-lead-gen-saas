#!/bin/bash
# Backup PostgreSQL database

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="./backups"
BACKUP_FILE="$BACKUP_DIR/lead_gen_backup_$TIMESTAMP.sql"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Starting database backup..."

# Use docker-compose to run pg_dump
docker-compose exec -T postgres pg_dump -U lead_gen_user -d lead_gen_db > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✓ Backup successful: $BACKUP_FILE"
    
    # Compress backup
    gzip "$BACKUP_FILE"
    echo "✓ Compressed: ${BACKUP_FILE}.gz"
    
    # Keep only last 7 backups
    ls -t "$BACKUP_DIR"/*.gz | tail -n +8 | xargs -r rm
    echo "✓ Old backups cleaned (keeping last 7)"
    
    exit 0
else
    echo "✗ Backup failed"
    rm -f "$BACKUP_FILE"
    exit 1
fi
