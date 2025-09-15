#!/bin/bash
# Deploy optimized Phygitals scraper to EC2
# Usage: ./deploy_to_ec2.sh [EC2_IP] [USERNAME]

set -e  # Exit on any error

# Configuration
EC2_IP=${1:-"your-ec2-ip"}
USERNAME=${2:-"ubuntu"}
REMOTE_DIR="/home/$USERNAME/pokev2"
LOCAL_DIR="."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Deploying Phygitals Scraper to EC2${NC}"
echo -e "${BLUE}=====================================${NC}"
echo "EC2 IP: $EC2_IP"
echo "Username: $USERNAME"
echo "Remote Directory: $REMOTE_DIR"
echo ""

# Check if required files exist locally
echo -e "${YELLOW}📋 Checking local files...${NC}"
required_files=("database.py" "scraper.py" "app.py" "monitor.py" "start.ps1" "docker-compose.yaml" "Dockerfile.scraper" "Dockerfile.webapp" "requirements.txt" "README.md")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Missing required file: $file${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✅ All required files found${NC}"

# Create remote directory if it doesn't exist
echo -e "${YELLOW}📁 Creating remote directory...${NC}"
ssh $USERNAME@$EC2_IP "mkdir -p $REMOTE_DIR"

# Stop any running services
echo -e "${YELLOW}🛑 Stopping existing services...${NC}"
ssh $USERNAME@$EC2_IP "cd $REMOTE_DIR && docker-compose down 2>/dev/null || true"

# Backup existing files (if any)
echo -e "${YELLOW}💾 Creating backup...${NC}"
ssh $USERNAME@$EC2_IP "cd $REMOTE_DIR && mkdir -p backup_$(date +%Y%m%d_%H%M%S) && cp -r . backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true"

# Copy optimized files to EC2
echo -e "${YELLOW}📤 Copying optimized files...${NC}"
scp database.py $USERNAME@$EC2_IP:$REMOTE_DIR/
scp scraper.py $USERNAME@$EC2_IP:$REMOTE_DIR/
scp app.py $USERNAME@$EC2_IP:$REMOTE_DIR/
scp monitor.py $USERNAME@$EC2_IP:$REMOTE_DIR/
scp start.ps1 $USERNAME@$EC2_IP:$REMOTE_DIR/
scp docker-compose.yaml $USERNAME@$EC2_IP:$REMOTE_DIR/
scp Dockerfile.scraper $USERNAME@$EC2_IP:$REMOTE_DIR/
scp Dockerfile.webapp $USERNAME@$EC2_IP:$REMOTE_DIR/
scp requirements.txt $USERNAME@$EC2_IP:$REMOTE_DIR/
scp README.md $USERNAME@$EC2_IP:$REMOTE_DIR/

# Copy templates directory if it exists
if [ -d "templates" ]; then
    echo -e "${YELLOW}📤 Copying templates directory...${NC}"
    scp -r templates $USERNAME@$EC2_IP:$REMOTE_DIR/
fi

# Set proper permissions
echo -e "${YELLOW}🔐 Setting permissions...${NC}"
ssh $USERNAME@$EC2_IP "cd $REMOTE_DIR && chmod +x *.py *.sh 2>/dev/null || true"

# Install Python dependencies
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
ssh $USERNAME@$EC2_IP "cd $REMOTE_DIR && pip3 install -r requirements.txt"

# Build and start Docker services
echo -e "${YELLOW}🐳 Building and starting Docker services...${NC}"
ssh $USERNAME@$EC2_IP "cd $REMOTE_DIR && docker-compose build"
ssh $USERNAME@$EC2_IP "cd $REMOTE_DIR && docker-compose up -d"

# Wait for services to start
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 10

# Run health check
echo -e "${YELLOW}🔍 Running health check...${NC}"
ssh $USERNAME@$EC2_IP "cd $REMOTE_DIR && python3 monitor.py"

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${BLUE}🌐 Web app should be available at: http://$EC2_IP:5001${NC}"
echo -e "${BLUE}📊 Monitor with: ssh $USERNAME@$EC2_IP 'cd $REMOTE_DIR && python3 monitor.py'${NC}"
