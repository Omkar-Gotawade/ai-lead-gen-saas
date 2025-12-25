#!/bin/bash
# Database restore script for AI Lead Gen SaaS
# Usage: ./restore.sh <backup_file>

if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup_file>"
    echo ""
    echo "Available backups:"
    ls -lh ./backups/*.sql.gz
    exit 1
fi

BACKUP_FILE=$1
CONTAINER_NAME="ai-lead-gen-saas-postgres-1"

echo "⚠️  WARNING: This will overwrite the current database!"
echo "Backup file: $BACKUP_FILE"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo ""
echo "Starting database restore..."

# Check if file is gzipped
if [[ $BACKUP_FILE == *.gz ]]; then
    echo "Decompressing backup file..."
    gunzip -c $BACKUP_FILE | docker exec -i $CONTAINER_NAME psql -U leadgen_user -d leadgen_db
else
    cat $BACKUP_FILE | docker exec -i $CONTAINER_NAME psql -U leadgen_user -d leadgen_db
fi

if [ $? -eq 0 ]; then
    echo "✅ Database restored successfully!"
else
    echo "❌ Restore failed!"
    exit 1
fi
