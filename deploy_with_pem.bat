@echo off
REM Deploy optimized Phygitals scraper to EC2 using PEM key
REM Usage: deploy_with_pem.bat EC2_IP PEM_KEY_PATH USERNAME

set EC2_IP=%1
set PEM_KEY=%2
set USERNAME=%3
set REMOTE_DIR=/home/%USERNAME%/pokev2

if "%EC2_IP%"=="" (
    echo Usage: deploy_with_pem.bat EC2_IP PEM_KEY_PATH USERNAME
    echo Example: deploy_with_pem.bat 51.20.73.162 "C:\path\to\your-key.pem" ubuntu
    exit /b 1
)

if "%PEM_KEY%"=="" (
    echo Usage: deploy_with_pem.bat EC2_IP PEM_KEY_PATH USERNAME
    echo Example: deploy_with_pem.bat 51.20.73.162 "C:\path\to\your-key.pem" ubuntu
    exit /b 1
)

if "%USERNAME%"=="" (
    set USERNAME=ubuntu
)

if not exist "%PEM_KEY%" (
    echo PEM key not found: %PEM_KEY%
    exit /b 1
)

echo Deploying Phygitals Scraper to EC2 using PEM key
echo ================================================
echo EC2 IP: %EC2_IP%
echo PEM Key: %PEM_KEY%
echo Username: %USERNAME%
echo Remote Directory: %REMOTE_DIR%
echo.

echo Testing SSH connection...
ssh -i "%PEM_KEY%" %USERNAME%@%EC2_IP% "echo SSH connection successful"
if errorlevel 1 (
    echo SSH connection failed. Check your PEM key and EC2 IP.
    exit /b 1
)

echo Creating remote directory...
ssh -i "%PEM_KEY%" %USERNAME%@%EC2_IP% "mkdir -p %REMOTE_DIR%"

echo Stopping existing services...
ssh -i "%PEM_KEY%" %USERNAME%@%EC2_IP% "cd %REMOTE_DIR%; docker-compose down 2>/dev/null; true"

echo Copying files...
scp -i "%PEM_KEY%" database.py %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
scp -i "%PEM_KEY%" scraper.py %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
scp -i "%PEM_KEY%" app.py %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
scp -i "%PEM_KEY%" monitor.py %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
scp -i "%PEM_KEY%" start.ps1 %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
scp -i "%PEM_KEY%" docker-compose.yaml %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
scp -i "%PEM_KEY%" Dockerfile.scraper %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
scp -i "%PEM_KEY%" Dockerfile.webapp %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
scp -i "%PEM_KEY%" requirements.txt %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
scp -i "%PEM_KEY%" README.md %USERNAME%@%EC2_IP%:%REMOTE_DIR%/

if exist templates (
    echo Copying templates directory...
    scp -i "%PEM_KEY%" -r templates %USERNAME%@%EC2_IP%:%REMOTE_DIR%/
)

echo Setting permissions...
ssh -i "%PEM_KEY%" %USERNAME%@%EC2_IP% "cd %REMOTE_DIR%; chmod +x *.py *.sh 2>/dev/null; true"

echo Installing Python dependencies...
ssh -i "%PEM_KEY%" %USERNAME%@%EC2_IP% "cd %REMOTE_DIR%; pip3 install -r requirements.txt"

echo Building and starting Docker services...
ssh -i "%PEM_KEY%" %USERNAME%@%EC2_IP% "cd %REMOTE_DIR%; docker-compose build"
ssh -i "%PEM_KEY%" %USERNAME%@%EC2_IP% "cd %REMOTE_DIR%; docker-compose up -d"

echo Waiting for services to start...
timeout /t 10 /nobreak >nul

echo Running health check...
ssh -i "%PEM_KEY%" %USERNAME%@%EC2_IP% "cd %REMOTE_DIR%; python3 monitor.py"

echo Deployment completed successfully!
echo Web app should be available at: http://%EC2_IP%:5001
echo Monitor with: ssh -i "%PEM_KEY%" %USERNAME%@%EC2_IP% "cd %REMOTE_DIR%; python3 monitor.py"
