@echo off
echo 🚀 Updating Production Docker containers with pagination improvements...

echo.
echo 📦 Stopping existing containers...
docker-compose -f docker-compose.prod.yaml down

echo.
echo 🗑️ Removing old images...
docker image prune -f

echo.
echo 🔨 Building new production images...
docker-compose -f docker-compose.prod.yaml build --no-cache

echo.
echo 🚀 Starting updated production containers...
docker-compose -f docker-compose.prod.yaml up -d

echo.
echo ✅ Production Docker update completed!
echo.
echo 🌐 Webapp available at: http://localhost:80
echo 📊 Database available at: localhost:3306
echo.
echo 📋 Container status:
docker-compose -f docker-compose.prod.yaml ps

echo.
echo 📝 To view logs:
echo   docker-compose -f docker-compose.prod.yaml logs -f webapp
echo   docker-compose -f docker-compose.prod.yaml logs -f database
echo.
pause
