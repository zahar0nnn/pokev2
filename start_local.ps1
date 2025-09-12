# PowerShell script for starting the application locally
Write-Host "🚀 Starting Phygitals Webapp locally..." -ForegroundColor Green

Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "🚀 Starting Flask application..." -ForegroundColor Yellow
Write-Host "🌐 Webapp will be available at: http://localhost:5001" -ForegroundColor Cyan
Write-Host "📊 Make sure MySQL is running on localhost:3306" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow
Write-Host ""

python app.py
