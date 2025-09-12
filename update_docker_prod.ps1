# PowerShell script for updating Production Docker containers
Write-Host "🚀 Updating Production Docker containers with pagination improvements..." -ForegroundColor Green

Write-Host ""
Write-Host "📦 Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.prod.yaml down

Write-Host ""
Write-Host "🗑️ Removing old images..." -ForegroundColor Yellow
docker image prune -f

Write-Host ""
Write-Host "🔨 Building new production images..." -ForegroundColor Yellow
docker-compose -f docker-compose.prod.yaml build --no-cache

Write-Host ""
Write-Host "🚀 Starting updated production containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.prod.yaml up -d

Write-Host ""
Write-Host "✅ Production Docker update completed!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Webapp available at: http://localhost:80" -ForegroundColor Cyan
Write-Host "📊 Database available at: localhost:3306" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Container status:" -ForegroundColor Yellow
docker-compose -f docker-compose.prod.yaml ps

Write-Host ""
Write-Host "📝 To view logs:" -ForegroundColor Yellow
Write-Host "  docker-compose -f docker-compose.prod.yaml logs -f webapp" -ForegroundColor Gray
Write-Host "  docker-compose -f docker-compose.prod.yaml logs -f database" -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter to continue"
