# Deploy optimized Phygitals scraper to EC2
# Usage: .\deploy_to_ec2_fixed.ps1 -EC2IP "your-ec2-ip" -Username "ubuntu"

param(
    [Parameter(Mandatory=$true)]
    [string]$EC2IP,
    
    [Parameter(Mandatory=$false)]
    [string]$Username = "ubuntu",
    
    [Parameter(Mandatory=$false)]
    [string]$RemoteDir = "/home/$Username/pokev2"
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "🚀 Deploying Phygitals Scraper to EC2" -ForegroundColor Blue
Write-Host "=====================================" -ForegroundColor Blue
Write-Host "EC2 IP: $EC2IP"
Write-Host "Username: $Username"
Write-Host "Remote Directory: $RemoteDir"
Write-Host ""

# Check if required files exist locally
Write-Host "📋 Checking local files..." -ForegroundColor Yellow
$requiredFiles = @("database.py", "scraper.py", "app.py", "monitor.py", "start.ps1", "docker-compose.yaml", "Dockerfile.scraper", "Dockerfile.webapp", "requirements.txt", "README.md")

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "❌ Missing required file: $file" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ All required files found" -ForegroundColor Green

# Create remote directory if it doesn't exist
Write-Host "📁 Creating remote directory..." -ForegroundColor Yellow
ssh $Username@$EC2IP "mkdir -p $RemoteDir"

# Stop any running services
Write-Host "🛑 Stopping existing services..." -ForegroundColor Yellow
ssh $Username@$EC2IP "cd $RemoteDir; docker-compose down 2>/dev/null; true"

# Backup existing files (if any)
Write-Host "💾 Creating backup..." -ForegroundColor Yellow
$backupDir = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
ssh $Username@$EC2IP "cd $RemoteDir; mkdir -p $backupDir; cp -r . $backupDir/ 2>/dev/null; true"

# Copy optimized files to EC2
Write-Host "📤 Copying optimized files..." -ForegroundColor Yellow
scp database.py "${Username}@${EC2IP}:${RemoteDir}/"
scp scraper.py "${Username}@${EC2IP}:${RemoteDir}/"
scp app.py "${Username}@${EC2IP}:${RemoteDir}/"
scp monitor.py "${Username}@${EC2IP}:${RemoteDir}/"
scp start.ps1 "${Username}@${EC2IP}:${RemoteDir}/"
scp docker-compose.yaml "${Username}@${EC2IP}:${RemoteDir}/"
scp Dockerfile.scraper "${Username}@${EC2IP}:${RemoteDir}/"
scp Dockerfile.webapp "${Username}@${EC2IP}:${RemoteDir}/"
scp requirements.txt "${Username}@${EC2IP}:${RemoteDir}/"
scp README.md "${Username}@${EC2IP}:${RemoteDir}/"

# Copy templates directory if it exists
if (Test-Path "templates") {
    Write-Host "📤 Copying templates directory..." -ForegroundColor Yellow
    scp -r templates "${Username}@${EC2IP}:${RemoteDir}/"
}

# Set proper permissions
Write-Host "🔐 Setting permissions..." -ForegroundColor Yellow
ssh $Username@$EC2IP "cd $RemoteDir; chmod +x *.py *.sh 2>/dev/null; true"

# Install Python dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
ssh $Username@$EC2IP "cd $RemoteDir; pip3 install -r requirements.txt"

# Build and start Docker services
Write-Host "🐳 Building and starting Docker services..." -ForegroundColor Yellow
ssh $Username@$EC2IP "cd $RemoteDir; docker-compose build"
ssh $Username@$EC2IP "cd $RemoteDir; docker-compose up -d"

# Wait for services to start
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Run health check
Write-Host "🔍 Running health check..." -ForegroundColor Yellow
ssh $Username@$EC2IP "cd $RemoteDir; python3 monitor.py"

Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
Write-Host "🌐 Web app should be available at: http://$EC2IP:5001" -ForegroundColor Blue
Write-Host "📊 Monitor with: ssh $Username@$EC2IP 'cd $RemoteDir; python3 monitor.py'" -ForegroundColor Blue
