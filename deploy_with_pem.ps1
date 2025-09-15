# Deploy optimized Phygitals scraper to EC2 using PEM key
# Usage: .\deploy_with_pem.ps1 -EC2IP "your-ec2-ip" -PemKey "path/to/key.pem" -Username "ubuntu"

param(
    [Parameter(Mandatory=$true)]
    [string]$EC2IP,
    
    [Parameter(Mandatory=$true)]
    [string]$PemKey,
    
    [Parameter(Mandatory=$false)]
    [string]$Username = "ubuntu"
)

$RemoteDir = "/home/$Username/pokev2"

Write-Host "Deploying Phygitals Scraper to EC2 using PEM key" -ForegroundColor Blue
Write-Host "EC2 IP: $EC2IP"
Write-Host "PEM Key: $PemKey"
Write-Host "Username: $Username"
Write-Host "Remote Directory: $RemoteDir"
Write-Host ""

# Check if PEM key exists
if (-not (Test-Path $PemKey)) {
    Write-Host "PEM key not found: $PemKey" -ForegroundColor Red
    exit 1
}

# Check if required files exist locally
Write-Host "Checking local files..." -ForegroundColor Yellow
$requiredFiles = @("database.py", "scraper.py", "app.py", "monitor.py", "start.ps1", "docker-compose.yaml", "Dockerfile.scraper", "Dockerfile.webapp", "requirements.txt", "README.md")

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "Missing required file: $file" -ForegroundColor Red
        exit 1
    }
}
Write-Host "All required files found" -ForegroundColor Green

# Test SSH connection first
Write-Host "Testing SSH connection..." -ForegroundColor Yellow
ssh -i $PemKey $Username@$EC2IP "echo 'SSH connection successful'"
if ($LASTEXITCODE -ne 0) {
    Write-Host "SSH connection failed. Check your PEM key and EC2 IP." -ForegroundColor Red
    exit 1
}

# Create remote directory
Write-Host "Creating remote directory..." -ForegroundColor Yellow
ssh -i $PemKey $Username@$EC2IP "mkdir -p $RemoteDir"

# Stop any running services
Write-Host "Stopping existing services..." -ForegroundColor Yellow
ssh -i $PemKey $Username@$EC2IP "cd $RemoteDir; docker-compose down 2>/dev/null; true"

# Copy files
Write-Host "Copying files..." -ForegroundColor Yellow
scp -i $PemKey database.py "${Username}@${EC2IP}:${RemoteDir}/"
scp -i $PemKey scraper.py "${Username}@${EC2IP}:${RemoteDir}/"
scp -i $PemKey app.py "${Username}@${EC2IP}:${RemoteDir}/"
scp -i $PemKey monitor.py "${Username}@${EC2IP}:${RemoteDir}/"
scp -i $PemKey start.ps1 "${Username}@${EC2IP}:${RemoteDir}/"
scp -i $PemKey docker-compose.yaml "${Username}@${EC2IP}:${RemoteDir}/"
scp -i $PemKey Dockerfile.scraper "${Username}@${EC2IP}:${RemoteDir}/"
scp -i $PemKey Dockerfile.webapp "${Username}@${EC2IP}:${RemoteDir}/"
scp -i $PemKey requirements.txt "${Username}@${EC2IP}:${RemoteDir}/"
scp -i $PemKey README.md "${Username}@${EC2IP}:${RemoteDir}/"

if (Test-Path "templates") {
    Write-Host "Copying templates directory..." -ForegroundColor Yellow
    scp -i $PemKey -r templates "${Username}@${EC2IP}:${RemoteDir}/"
}

# Set permissions
Write-Host "Setting permissions..." -ForegroundColor Yellow
ssh -i $PemKey $Username@$EC2IP "cd $RemoteDir; chmod +x *.py *.sh 2>/dev/null; true"

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
ssh -i $PemKey $Username@$EC2IP "cd $RemoteDir; pip3 install -r requirements.txt"

# Build and start services
Write-Host "Building and starting Docker services..." -ForegroundColor Yellow
ssh -i $PemKey $Username@$EC2IP "cd $RemoteDir; docker-compose build"
ssh -i $PemKey $Username@$EC2IP "cd $RemoteDir; docker-compose up -d"

# Wait and check
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "Running health check..." -ForegroundColor Yellow
ssh -i $PemKey $Username@$EC2IP "cd $RemoteDir; python3 monitor.py"

Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "Web app should be available at: http://$EC2IP:5001" -ForegroundColor Blue
Write-Host "Monitor with: ssh -i $PemKey $Username@$EC2IP 'cd $RemoteDir; python3 monitor.py'" -ForegroundColor Blue
