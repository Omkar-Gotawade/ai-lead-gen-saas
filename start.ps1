# AI Lead Generation SaaS - Quick Start Script
Write-Host "================================" -ForegroundColor Cyan
Write-Host "AI Lead Generation SaaS" -ForegroundColor Cyan
Write-Host "Week 0 + Week 1 Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker status
Write-Host "[0/4] Checking Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "      Docker is running" -ForegroundColor Green
} catch {
    Write-Host "      Docker is not running!" -ForegroundColor Red
    Write-Host "      Please start Docker Desktop and try again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[1/4] Starting Docker containers..." -ForegroundColor Yellow
docker-compose up -d --build

Write-Host ""
Write-Host "[2/4] Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "[3/4] Running database migrations..." -ForegroundColor Yellow
docker-compose exec -T backend alembic upgrade head

Write-Host ""
Write-Host "[4/4] Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Application is ready!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend: " -NoNewline
Write-Host "http://localhost:5173" -ForegroundColor Green
Write-Host "Backend:  " -NoNewline
Write-Host "http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs: " -NoNewline
Write-Host "http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "To view logs: " -NoNewline
Write-Host "docker-compose logs -f" -ForegroundColor Yellow
Write-Host "To stop:      " -NoNewline
Write-Host "docker-compose down" -ForegroundColor Yellow
Write-Host ""

Read-Host "Press Enter to exit"
