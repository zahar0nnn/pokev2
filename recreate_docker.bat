@echo off
echo 🐳 Recreating Docker Containers
echo ===============================

echo.
echo 🔍 Checking Docker...
docker --version
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker not found!
    echo 💡 Please install Docker Desktop first
    pause
    exit /b 1
)

echo.
echo ✅ Docker found!
echo.
echo 🛑 Stopping existing containers...
docker-compose down -v

echo.
echo 🧹 Cleaning up...
docker system prune -f

echo.
echo 🚀 Building and starting new containers...
docker-compose up -d --build

echo.
echo ⏳ Waiting for services to initialize...
echo 💡 This may take 1-2 minutes...
timeout /t 30 /nobreak > nul

echo.
echo 🔍 Checking container status...
docker ps

echo.
echo 🌐 Web app should be available at:
echo    http://localhost:5001
echo    http://127.0.0.1:5001
echo.
echo 💡 If you get errors, check logs:
echo    docker logs phygitals-webapp
echo    docker logs phygitals-database
echo.
pause
