@echo off
REM AWS EC2 Setup Script for Windows
REM This script helps prepare your project for AWS EC2 deployment

echo 🚀 Preparing Phygitals Scraper for AWS EC2 deployment...

REM Check if required files exist
if not exist "docker-compose.prod.yaml" (
    echo ❌ docker-compose.prod.yaml not found!
    echo Please ensure all required files are present.
    pause
    exit /b 1
)

if not exist "Dockerfile.webapp.prod" (
    echo ❌ Dockerfile.webapp.prod not found!
    echo Please ensure all required files are present.
    pause
    exit /b 1
)

if not exist "Dockerfile.scraper.prod" (
    echo ❌ Dockerfile.scraper.prod not found!
    echo Please ensure all required files are present.
    pause
    exit /b 1
)

echo ✅ All required files found!

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file from template...
    copy env.example .env
    echo ⚠️  Please edit .env file with your actual passwords!
    echo Opening .env file for editing...
    notepad .env
    echo Press any key after updating .env file...
    pause > nul
)

echo ✅ Environment file ready!

REM Test Docker build locally
echo 🐳 Testing Docker build locally...
docker-compose -f docker-compose.prod.yaml build

if %errorlevel% neq 0 (
    echo ❌ Docker build failed!
    echo Please check your Docker configuration.
    pause
    exit /b 1
)

echo ✅ Docker build successful!

echo 🎉 Project is ready for AWS EC2 deployment!
echo.
echo 📋 Next steps:
echo 1. Upload your project to AWS EC2 instance
echo 2. Run the deploy-aws.sh script on the EC2 instance
echo 3. Access your application at http://your-ec2-ip
echo.
echo 📁 Files to upload to EC2:
echo - All project files
echo - .env (with your passwords)
echo - deploy-aws.sh
echo.
echo Press any key to exit...
pause > nul
