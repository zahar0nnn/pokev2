@echo off
echo 🚀 Updating Docker containers with pagination improvements...

echo.
echo 📦 Stopping existing containers...
docker-compose down

echo.
echo 🗑️ Removing old images...
docker image prune -f

echo.
echo 🔨 Building new images...
docker-compose build --no-cache

echo.
echo 🚀 Starting updated containers...
docker-compose up -d

echo.
echo ✅ Docker update completed!
echo.
echo 🌐 Webapp available at: http://localhost:5001
echo 📊 Database available at: localhost:3306
echo.
echo 📋 Container status:
docker-compose ps

echo.
echo 📝 To view logs:
echo   docker-compose logs -f webapp
echo   docker-compose logs -f database
echo.
pause
