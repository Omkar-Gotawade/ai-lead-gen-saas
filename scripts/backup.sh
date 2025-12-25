#!/bin/bash
# Database backup script for AI Lead Gen SaaS
# Usage: ./backup.sh

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/leadgen_backup_$TIMESTAMP.sql"
CONTAINER_NAME="ai-lead-gen-saas-postgres-1"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

echo "Starting database backup..."
echo "Timestamp: $TIMESTAMP"

# Run pg_dump inside the container
docker exec -t $CONTAINER_NAME pg_dump -U leadgen_user -d leadgen_db > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Backup completed successfully!"
    echo "📁 Backup file: $BACKUP_FILE"
    
    # Compress the backup
    gzip $BACKUP_FILE
    echo "📦 Compressed to: ${BACKUP_FILE}.gz"
    
    # Delete backups older than 7 days
    find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
    echo "🧹 Cleaned up old backups (>7 days)"
    
    # Show backup size
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
    echo "💾 Backup size: $BACKUP_SIZE"
else
    echo "❌ Backup failed!"
    exit 1
fi

echo ""
echo "📊 Recent backups:"
ls -lht $BACKUP_DIR | head -5
