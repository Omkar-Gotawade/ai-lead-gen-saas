# PowerShell Database Restore Script for AI Lead Gen SaaS
# Usage: .\restore.ps1 <backup_file>

param(
    [Parameter(Mandatory=$false)]
    [string]$BackupFile
)

$ContainerName = "ai-lead-gen-saas-postgres-1"

if (!$BackupFile) {
    Write-Host "Usage: .\restore.ps1 <backup_file>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Available backups:" -ForegroundColor Cyan
    Get-ChildItem .\backups\*.zip | Format-Table Name, Length, LastWriteTime
    exit 1
}

Write-Host "⚠️  WARNING: This will overwrite the current database!" -ForegroundColor Yellow
Write-Host "Backup file: $BackupFile"
$Confirm = Read-Host "Are you sure you want to continue? (yes/no)"

if ($Confirm -ne "yes") {
    Write-Host "Restore cancelled."
    exit 0
}

Write-Host ""
Write-Host "Starting database restore..." -ForegroundColor Cyan

# Check if file is zipped
if ($BackupFile -match "\.zip$") {
    Write-Host "Extracting backup file..."
    $TempFile = "$env:TEMP\leadgen_restore_temp.sql"
    Expand-Archive -Path $BackupFile -DestinationPath $env:TEMP -Force
    $ExtractedFile = Get-ChildItem "$env:TEMP\leadgen_backup_*.sql" | Select-Object -First 1
    
    Get-Content $ExtractedFile.FullName | docker exec -i $ContainerName psql -U leadgen_user -d leadgen_db
    
    Remove-Item $ExtractedFile.FullName
} else {
    Get-Content $BackupFile | docker exec -i $ContainerName psql -U leadgen_user -d leadgen_db
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database restored successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Restore failed!" -ForegroundColor Red
    exit 1
}
