@echo off
echo 🐳 Docker Pokemon Scraper & Web App
echo ===================================

echo.
echo 🔍 Running Docker diagnostic...
python docker_diagnostic.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Docker diagnostic failed!
    echo 💡 Please check the issues above.
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Docker diagnostic passed!
echo.
echo 🚀 Starting Docker services...
docker-compose up -d

echo.
echo ⏳ Waiting for services to initialize...
timeout /t 10 /nobreak > nul

echo.
echo 🌐 Web app should be available at:
echo    http://localhost:5001
echo    http://127.0.0.1:5001
echo.
echo 💡 To stop services: docker-compose down
echo 💡 To view logs: docker-compose logs -f
echo.
pause
