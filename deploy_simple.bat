@echo off
REM Simple Windows batch file for EC2 deployment
REM Usage: deploy_simple.bat 51.20.73.162 ubuntu

set EC2_IP=%1
set USERNAME=%2
set REMOTE_DIR=/home/%USERNAME%/pokev2

if "%EC2_IP%"=="" (
    echo Usage: deploy_simple.bat EC2_IP USERNAME
    echo Example: deploy_simple.bat 51.20.73.162 ubuntu
    exit /b 1
)

if "%USERNAME%"=="" (
    set USERNAME=ubuntu
)

echo 🚀 Deploying Phygitals Scraper to EC2
echo =====================================
echo EC2 IP: %EC2_IP%
echo Username: %USERNAME%
echo Remote Directory: %REMOTE_DIR%
echo.

echo 📁 Creating remote directory...
ssh %USERNAME%@%EC2_IP% "mkdir -p %REMOTE_DIR%"

echo 🛑 Stopping existing services...
ssh %USERNAME%@%EC2_IP% "cd %REMOTE_DIR%; docker-compose down 2>/dev/null; true"

echo 💾 Creating backup...
ssh %USERNAME%@%EC2_IP% "cd %REMOTE_DIR%; mkdir -p backup_$(date +%%Y%%m%%d_%%H%%M%%S); cp -r . backup_$(date +%%Y%%m%%d_%%H%%M%%S)/ 2>/dev/null; true"

echo 📤 Copying optimized files...
scp database.py %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
scp scraper.py %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
scp app.py %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
scp monitor.py %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
scp start.ps1 %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
scp docker-compose.yaml %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
scp Dockerfile.scraper %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
scp Dockerfile.webapp %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
scp requirements.txt %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
scp README.md %USERNAME%@%EC2_IP%:%REMOTE_DIR%/

if exist templates (
    echo 📤 Copying templates directory...
    scp -r templates %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
)

echo 🔐 Setting permissions...
ssh %USERNAME%@%EC2_IP% "cd %REMOTE_DIR%; chmod +x *.py *.sh 2>/dev/null; true"

echo 📦 Installing Python dependencies...
ssh %USERNAME%@%EC2_IP% "cd %REMOTE_DIR%; pip3 install -r requirements.txt"

echo 🐳 Building and starting Docker services...
ssh %USERNAME%@%EC2_IP% "cd %REMOTE_DIR%; docker-compose build"
ssh %USERNAME%@%EC2_IP% "cd %REMOTE_DIR%; docker-compose up -d"

echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

echo 🔍 Running health check...
ssh %USERNAME%@%EC2_IP% "cd %REMOTE_DIR%; python3 monitor.py"

echo ✅ Deployment completed successfully!
echo 🌐 Web app should be available at: http://%EC2_IP%:5001
echo 📊 Monitor with: ssh %USERNAME%@%EC2_IP% "cd %REMOTE_DIR%; python3 monitor.py"
