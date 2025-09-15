# Optimized Phygitals Scraper Startup Script
Write-Host "🚀 Starting Optimized Phygitals Scraper" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Check if required files exist
$requiredFiles = @("scraper.py", "database.py", "app.py", "monitor.py")
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "❌ $file not found!" -ForegroundColor Red
        Write-Host "💡 Make sure you're in the project directory" -ForegroundColor Yellow
        exit 1
    }
}

# Install requirements if needed
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

Write-Host "📦 Installing requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "🔍 Testing database connection..." -ForegroundColor Yellow
python -c "from database import Database; db = Database(); db.setup_database(); print('✅ Database setup complete')"

Write-Host "🔍 Starting scraper..." -ForegroundColor Green
Write-Host "💡 Press Ctrl+C to stop the scraper" -ForegroundColor Yellow
Write-Host "💡 Run 'python app.py' in another terminal to start the web app" -ForegroundColor Yellow
Write-Host ""

python scraper.py

Write-Host "✅ Done!" -ForegroundColor Green
