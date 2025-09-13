#!/bin/bash

# Docker Installation Script for Ubuntu EC2
# This script installs Docker and Docker Compose on Ubuntu EC2 instances

set -e

echo "🐳 Installing Docker on Ubuntu EC2..."

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

# Check if running on Ubuntu
if ! grep -q "Ubuntu" /etc/os-release; then
    print_error "This script is designed for Ubuntu. Please run on Ubuntu or modify for your OS."
    exit 1
fi

# Check if Docker is already installed
if command -v docker &> /dev/null; then
    print_warning "Docker is already installed. Checking status..."
    if sudo systemctl is-active --quiet docker; then
        print_status "Docker service is running"
    else
        print_warning "Docker service is not running. Starting..."
        sudo systemctl start docker
    fi
    exit 0
fi

# Update package index
print_status "Updating package index..."
sudo apt-get update -y

# Install required packages
print_status "Installing required packages..."
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release software-properties-common

# Add Docker's official GPG key
print_status "Adding Docker's GPG key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
print_status "Adding Docker repository..."
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index with Docker repository
print_status "Updating package index with Docker repository..."
sudo apt-get update -y

# Install Docker Engine
print_status "Installing Docker Engine..."
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker service
print_status "Starting Docker service..."
sudo systemctl start docker

# Enable Docker to start on boot
print_status "Enabling Docker to start on boot..."
sudo systemctl enable docker

# Add user to docker group
print_status "Adding user $USER to docker group..."
sudo usermod -aG docker $USER

# Wait a moment for group changes to take effect
sleep 2

# Check Docker service status
print_status "Checking Docker service status..."
if sudo systemctl is-active --quiet docker; then
    print_status "✅ Docker service is running"
else
    print_error "❌ Docker service failed to start"
    sudo systemctl status docker
    exit 1
fi

# Test Docker installation
print_status "Testing Docker installation..."
if sudo docker --version > /dev/null 2>&1; then
    DOCKER_VERSION=$(sudo docker --version)
    print_status "✅ Docker installed successfully: $DOCKER_VERSION"
else
    print_error "❌ Docker installation failed"
    exit 1
fi

# Test Docker daemon
print_status "Testing Docker daemon..."
if sudo docker ps > /dev/null 2>&1; then
    print_status "✅ Docker daemon is working"
else
    print_error "❌ Docker daemon is not working"
    exit 1
fi

# Test with hello-world container
print_status "Testing with hello-world container..."
if sudo docker run --rm hello-world > /dev/null 2>&1; then
    print_status "✅ Docker container test successful"
else
    print_warning "⚠️  Docker container test failed, but Docker is installed"
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
fi

print_status "🎉 Docker installation completed successfully!"
print_status ""
print_status "📋 Next steps:"
print_status "1. Log out and back in, or run: newgrp docker"
print_status "2. Test Docker without sudo: docker --version"
print_status "3. Edit .env file with your passwords: nano .env"
print_status "4. Start services: docker-compose -f docker-compose.prod.yaml up -d"
print_status "5. Check status: docker-compose -f docker-compose.prod.yaml ps"
print_status ""
print_status "🔧 Useful commands:"
print_status "- Test Docker: docker --version && docker ps"
print_status "- Start services: docker-compose -f docker-compose.prod.yaml up -d"
print_status "- View logs: docker-compose -f docker-compose.prod.yaml logs -f"
print_status "- Stop services: docker-compose -f docker-compose.prod.yaml down"
