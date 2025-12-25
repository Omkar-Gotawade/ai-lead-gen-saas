# PowerShell Database Backup Script for AI Lead Gen SaaS
# Usage: .\backup.ps1

# Configuration
$BackupDir = ".\backups"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = "$BackupDir\leadgen_backup_$Timestamp.sql"
$ContainerName = "ai-lead-gen-saas-postgres-1"

# Create backup directory if it doesn't exist
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

Write-Host "Starting database backup..." -ForegroundColor Cyan
Write-Host "Timestamp: $Timestamp"

# Run pg_dump inside the container
docker exec -t $ContainerName pg_dump -U leadgen_user -d leadgen_db | Out-File -FilePath $BackupFile -Encoding utf8

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backup completed successfully!" -ForegroundColor Green
    Write-Host "📁 Backup file: $BackupFile"
    
    # Compress the backup
    Compress-Archive -Path $BackupFile -DestinationPath "$BackupFile.zip" -Force
    Remove-Item $BackupFile
    Write-Host "📦 Compressed to: $BackupFile.zip"
    
    # Delete backups older than 7 days
    Get-ChildItem $BackupDir -Filter "*.zip" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | Remove-Item
    Write-Host "🧹 Cleaned up old backups (>7 days)"
    
    # Show backup size
    $BackupSize = (Get-Item "$BackupFile.zip").Length / 1MB
    Write-Host "💾 Backup size: $([math]::Round($BackupSize, 2)) MB"
} else {
    Write-Host "❌ Backup failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📊 Recent backups:" -ForegroundColor Cyan
Get-ChildItem $BackupDir -Filter "*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | Format-Table Name, Length, LastWriteTime
