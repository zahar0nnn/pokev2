#!/bin/bash

# Docker Permission Fix Script for EC2
# This script fixes Docker permission issues on Ubuntu EC2 instances

set -e

echo "🔧 Fixing Docker permissions on EC2..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Don't run this script as root. Run as regular user with sudo access."
    exit 1
fi

# Add user to docker group
print_status "Adding user $USER to docker group..."
sudo usermod -aG docker $USER

# Restart Docker service
print_status "Restarting Docker service..."
sudo systemctl restart docker

# Wait a moment for Docker to restart
sleep 2

# Check Docker service status
print_status "Checking Docker service status..."
if sudo systemctl is-active --quiet docker; then
    print_status "✅ Docker service is running"
else
    print_error "❌ Docker service is not running"
    sudo systemctl status docker
    exit 1
fi

# Apply group changes
print_status "Applying group changes..."
newgrp docker << EOF
echo "Testing Docker access in new group context..."
docker --version
docker ps
echo "✅ Docker access test completed"
EOF

# Test Docker access
print_status "Testing Docker access..."
if docker --version > /dev/null 2>&1; then
    print_status "✅ Docker command works without sudo"
else
    print_warning "⚠️  Docker command still requires sudo. You may need to log out and back in."
fi

# Test Docker daemon access
print_status "Testing Docker daemon access..."
if docker ps > /dev/null 2>&1; then
    print_status "✅ Docker daemon access works"
else
    print_warning "⚠️  Docker daemon access may still have issues"
    print_warning "Try logging out and back in, or run: exec su -l \$USER"
fi

# Check if we're in the project directory
if [ -f "docker-compose.yaml" ] || [ -f "docker-compose.prod.yaml" ]; then
    print_status "Found Docker Compose files in current directory"
    
    # Check for .env file
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            print_warning "Creating .env file from template..."
            cp env.example .env
            print_warning "Please edit .env file with your actual passwords!"
            print_warning "Run: nano .env"
        else
            print_error "No env.example file found. Please create .env file manually."
        fi
    fi
    
    print_status "You can now run:"
    print_status "  docker-compose up -d"
    print_status "  or"
    print_status "  docker-compose -f docker-compose.prod.yaml up -d"
fi

print_status "🎉 Docker permission fix completed!"
print_status ""
print_status "📋 Next steps:"
print_status "1. If Docker still doesn't work, log out and back in"
print_status "2. Edit .env file with your passwords: nano .env"
print_status "3. Start services: docker-compose -f docker-compose.prod.yaml up -d"
print_status "4. Check status: docker-compose -f docker-compose.prod.yaml ps"
print_status "5. View logs: docker-compose -f docker-compose.prod.yaml logs -f"
