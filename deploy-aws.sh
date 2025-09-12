#!/bin/bash

# AWS EC2 Deployment Script for Phygitals Scraper
# This script automates the deployment process on AWS EC2

set -e  # Exit on any error

echo "🚀 Starting AWS EC2 deployment for Phygitals Scraper..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Update system
print_status "Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Docker
print_status "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    print_status "Docker installed successfully"
else
    print_warning "Docker is already installed"
fi

# Install Docker Compose
print_status "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed successfully"
else
    print_warning "Docker Compose is already installed"
fi

# Install additional tools
print_status "Installing additional tools..."
sudo apt-get install -y git htop tree nano curl wget

# Create application directory
print_status "Setting up application directory..."
sudo mkdir -p /opt/phygitals
sudo chown $USER:$USER /opt/phygitals
cd /opt/phygitals

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning "No .env file found. Creating from template..."
    if [ -f "env.example" ]; then
        cp env.example .env
        print_warning "Please edit .env file with your actual passwords before continuing!"
        print_warning "Run: nano .env"
        read -p "Press Enter after updating .env file..."
    else
        print_error "No env.example file found. Please create .env file manually."
        exit 1
    fi
fi

# Set up log rotation
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/phygitals > /dev/null << EOF
/opt/phygitals/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 $USER $USER
}
EOF

# Create logs directory
mkdir -p logs

# Create monitoring script
print_status "Creating monitoring script..."
cat > monitor.sh << 'EOF'
#!/bin/bash
echo "=== System Resources ==="
free -h
echo ""
echo "=== Disk Usage ==="
df -h
echo ""
echo "=== Docker Containers ==="
docker ps
echo ""
echo "=== Container Stats ==="
docker stats --no-stream
EOF

chmod +x monitor.sh

# Create backup script
print_status "Creating backup script..."
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/phygitals/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
echo "Backing up database..."
docker exec phygitals-mysql mysqldump -u root -p$MYSQL_ROOT_PASSWORD scraped_data > $BACKUP_DIR/database_$DATE.sql

# Backup application data
echo "Backing up application data..."
tar -czf $BACKUP_DIR/app_data_$DATE.tar.gz data/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh

# Create scraping script
print_status "Creating scraping script..."
cat > run_scraper.sh << 'EOF'
#!/bin/bash
cd /opt/phygitals
echo "Starting scraper at $(date)"
docker-compose -f docker-compose.prod.yaml run --rm scraper python scraper.py
echo "Scraper completed at $(date)"
EOF

chmod +x run_scraper.sh

# Build and start services
print_status "Building and starting services..."
docker-compose -f docker-compose.prod.yaml build
docker-compose -f docker-compose.prod.yaml up -d

# Wait for services to be healthy
print_status "Waiting for services to start..."
sleep 30

# Check service status
print_status "Checking service status..."
docker-compose -f docker-compose.prod.yaml ps

# Test web application
print_status "Testing web application..."
if curl -f http://localhost:5001/debug > /dev/null 2>&1; then
    print_status "✅ Web application is running successfully!"
    print_status "🌐 Access your application at: http://$(curl -s ifconfig.me)"
else
    print_warning "⚠️  Web application might not be ready yet. Check logs with: docker-compose logs webapp"
fi

# Set up automated backups
print_status "Setting up automated backups..."
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/phygitals/backup.sh") | crontab -

# Set up automated scraping (every 6 hours)
print_status "Setting up automated scraping..."
(crontab -l 2>/dev/null; echo "0 */6 * * * /opt/phygitals/run_scraper.sh") | crontab -

print_status "🎉 Deployment completed successfully!"
print_status ""
print_status "📋 Next steps:"
print_status "1. Access your web app: http://$(curl -s ifconfig.me)"
print_status "2. Check logs: docker-compose -f docker-compose.prod.yaml logs -f"
print_status "3. Monitor system: ./monitor.sh"
print_status "4. Run scraper manually: ./run_scraper.sh"
print_status "5. Check backups: ls -la backups/"
print_status ""
print_status "🔧 Useful commands:"
print_status "- View logs: docker-compose -f docker-compose.prod.yaml logs -f"
print_status "- Restart services: docker-compose -f docker-compose.prod.yaml restart"
print_status "- Stop services: docker-compose -f docker-compose.prod.yaml down"
print_status "- Update application: git pull && docker-compose -f docker-compose.prod.yaml build && docker-compose -f docker-compose.prod.yaml up -d"
