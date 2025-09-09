#!/bin/bash

# Ubuntu Setup Script for Phygitals Scraper
echo "🚀 Setting up Phygitals Scraper on Ubuntu..."

# Update package list
echo "📦 Updating package list..."
sudo apt update

# Install Python and pip if not already installed
echo "🐍 Installing Python and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Install MySQL Server
echo "🗄️ Installing MySQL Server..."
sudo apt install -y mysql-server

# Install additional dependencies
echo "📚 Installing additional dependencies..."
sudo apt install -y python3-dev libmysqlclient-dev build-essential

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up MySQL database
echo "🗄️ Setting up MySQL database..."
echo "Please run the following commands in MySQL:"
echo "sudo mysql -u root -p"
echo "CREATE DATABASE scraped_data;"
echo "CREATE USER 'root'@'localhost' IDENTIFIED BY 'my-secret-pw';"
echo "GRANT ALL PRIVILEGES ON scraped_data.* TO 'root'@'localhost';"
echo "FLUSH PRIVILEGES;"
echo "EXIT;"

echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start web server: python3 app.py"
echo "3. Start scraper (in another terminal): python3 scraper.py"
echo ""
echo "The web interface will be available at: http://localhost:5001"
