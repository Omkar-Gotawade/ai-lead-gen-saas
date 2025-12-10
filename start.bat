@echo off
echo ================================
echo AI Lead Generation SaaS
echo Week 0 + Week 1 Setup
echo ================================
echo.

echo [1/4] Starting Docker containers...
docker-compose up -d --build

echo.
echo [2/4] Waiting for services to be ready...
timeout /t 10 /nobreak > nul

echo.
echo [3/4] Running database migrations...
docker-compose exec -T backend alembic upgrade head

echo.
echo [4/4] Setup complete!
echo.
echo ================================
echo Application is ready!
echo ================================
echo.
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo To view logs: docker-compose logs -f
echo To stop:      docker-compose down
echo.

pause
