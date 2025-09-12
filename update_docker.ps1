# PowerShell script for updating Docker containers
Write-Host "🚀 Updating Docker containers with pagination improvements..." -ForegroundColor Green

Write-Host ""
Write-Host "📦 Stopping existing containers..." -ForegroundColor Yellow
docker-compose down

Write-Host ""
Write-Host "🗑️ Removing old images..." -ForegroundColor Yellow
docker image prune -f

Write-Host ""
Write-Host "🔨 Building new images..." -ForegroundColor Yellow
docker-compose build --no-cache

Write-Host ""
Write-Host "🚀 Starting updated containers..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "✅ Docker update completed!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Webapp available at: http://localhost:5001" -ForegroundColor Cyan
Write-Host "📊 Database available at: localhost:3306" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Container status:" -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "📝 To view logs:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f webapp" -ForegroundColor Gray
Write-Host "  docker-compose logs -f database" -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter to continue"
