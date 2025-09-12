# 🚀 AWS EC2 Deployment Guide for Phygitals Scraper

## 📋 **Overview**

This guide will help you deploy your Phygitals scraper project (scraper, database & web app) to AWS EC2. The project includes:
- **Scraper**: Python-based data scraper with multiprocessing
- **Database**: MySQL 8.0 with persistent storage
- **Web App**: Flask-based web interface with filtering and charts
- **Docker**: Complete containerized setup

## 🎯 **Prerequisites**

- AWS Account with EC2 access
- Basic knowledge of AWS EC2, Security Groups, and VPC
- Docker and Docker Compose installed locally (for building images)
- Git installed locally

## 🏗️ **Step 1: Prepare Your Project**

### 1.1 **Optimize Docker Configuration for AWS**

First, let's create an optimized docker-compose file for production:

```yaml
# docker-compose.prod.yaml
version: "3.8"

services:
  database:
    image: mysql:8.0
    container_name: phygitals-mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-your-secure-password-here}
      MYSQL_DATABASE: scraped_data
      MYSQL_USER: scraper
      MYSQL_PASSWORD: ${MYSQL_PASSWORD:-your-scraper-password-here}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
    command: --default-authentication-plugin=mysql_native_password
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${MYSQL_ROOT_PASSWORD:-your-secure-password-here}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  webapp:
    build:
      context: .
      dockerfile: Dockerfile.webapp
    container_name: phygitals-webapp
    depends_on:
      database:
        condition: service_healthy
    environment:
      MYSQL_HOST: database
      MYSQL_PORT: 3306
      MYSQL_USER: root
      MYSQL_PASSWORD: ${MYSQL_ROOT_PASSWORD:-your-secure-password-here}
      MYSQL_DATABASE: scraped_data
      FLASK_ENV: production
      FLASK_DEBUG: 0
    ports:
      - "80:5001"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/debug"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  mysql_data:
```

### 1.2 **Create Environment File**

Create `.env` file for production secrets:

```bash
# .env
MYSQL_ROOT_PASSWORD=your-super-secure-password-here
MYSQL_PASSWORD=your-scraper-password-here
```

### 1.3 **Create Production Dockerfile Optimizations**

Update your Dockerfiles for production:

```dockerfile
# Dockerfile.webapp.prod
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY app_fixed.py .
COPY database_config.py .
COPY templates/ templates/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5001

# Run the web application
CMD ["python", "app.py"]
```

## 🖥️ **Step 2: Launch EC2 Instance**

### 2.1 **Instance Configuration**

1. **Go to AWS EC2 Console**
2. **Click "Launch Instance"**
3. **Choose AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
4. **Instance Type**: 
   - **t2.micro** (Free tier) - for testing
   - **t3.small** or **t3.medium** - for production
5. **Key Pair**: Create or select an existing key pair
6. **Security Group**: Create new with these rules:
   - **SSH (22)**: Your IP only
   - **HTTP (80)**: 0.0.0.0/0 (for web access)
   - **Custom TCP (3306)**: Your IP only (for database access)

### 2.2 **Storage Configuration**

- **Root Volume**: 20-30 GB (gp3)
- **Additional Volume** (optional): 100+ GB for data storage

### 2.3 **Advanced Configuration**

- **IAM Role**: Create role with EC2 permissions (optional)
- **User Data**: Add initialization script (see below)

## 🔧 **Step 3: Instance Setup Script**

Create this user data script for automatic setup:

```bash
#!/bin/bash
# Update system
apt-get update -y
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Git
apt-get install -y git

# Install additional tools
apt-get install -y htop tree nano

# Create application directory
mkdir -p /opt/phygitals
chown ubuntu:ubuntu /opt/phygitals

# Set up log rotation
cat > /etc/logrotate.d/phygitals << EOF
/opt/phygitals/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 ubuntu ubuntu
}
EOF

# Reboot to ensure all updates are applied
reboot
```

## 📦 **Step 4: Deploy Your Application**

### 4.1 **Connect to Your Instance**

```bash
# Replace with your key file and instance IP
ssh -i "your-key.pem" ubuntu@your-ec2-ip-address
```

### 4.2 **Clone and Setup Project**

```bash
# Navigate to application directory
cd /opt/phygitals

# Clone your repository
git clone https://github.com/yourusername/pokev2.git .

# Or upload files using SCP
# scp -i "your-key.pem" -r ./pokev2/* ubuntu@your-ec2-ip:/opt/phygitals/
```

### 4.3 **Configure Environment**

```bash
# Create environment file
nano .env
# Add your production passwords:
# MYSQL_ROOT_PASSWORD=your-super-secure-password-here
# MYSQL_PASSWORD=your-scraper-password-here

# Set proper permissions
chmod 600 .env
chown ubuntu:ubuntu .env
```

### 4.4 **Build and Start Services**

```bash
# Build and start with production configuration
docker-compose -f docker-compose.prod.yaml up -d

# Check status
docker-compose -f docker-compose.prod.yaml ps

# View logs
docker-compose -f docker-compose.prod.yaml logs -f
```

## 🔒 **Step 5: Security Configuration**

### 5.1 **Update Security Groups**

1. **Go to EC2 → Security Groups**
2. **Edit your security group**:
   - **HTTP (80)**: 0.0.0.0/0 (for web access)
   - **HTTPS (443)**: 0.0.0.0/0 (if using SSL)
   - **SSH (22)**: Your IP only
   - **MySQL (3306)**: Your IP only (or remove if not needed externally)

### 5.2 **Configure Firewall (UFW)**

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow ssh

# Allow HTTP
sudo ufw allow 80

# Allow HTTPS (if using SSL)
sudo ufw allow 443

# Check status
sudo ufw status
```

### 5.3 **Set Up SSL (Optional but Recommended)**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 **Step 6: Monitoring and Logging**

### 6.1 **Set Up Logging**

```bash
# Create logs directory
mkdir -p /opt/phygitals/logs

# Update docker-compose.prod.yaml to include logging
# Add this to each service:
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 6.2 **Install Monitoring Tools**

```bash
# Install htop for system monitoring
sudo apt install htop -y

# Install Docker stats monitoring
sudo apt install docker-compose -y

# Create monitoring script
cat > /opt/phygitals/monitor.sh << 'EOF'
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

chmod +x /opt/phygitals/monitor.sh
```

### 6.3 **Set Up Automated Backups**

```bash
# Create backup script
cat > /opt/phygitals/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/phygitals/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
docker exec phygitals-mysql mysqldump -u root -p$MYSQL_ROOT_PASSWORD scraped_data > $BACKUP_DIR/database_$DATE.sql

# Backup application data
tar -czf $BACKUP_DIR/app_data_$DATE.tar.gz /opt/phygitals/data

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/phygitals/backup.sh

# Add to crontab for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/phygitals/backup.sh") | crontab -
```

## 🚀 **Step 7: Run the Scraper**

### 7.1 **Start Scraping**

```bash
# Run scraper once
docker-compose -f docker-compose.prod.yaml run --rm scraper python scraper.py

# Or run scraper in background
docker-compose -f docker-compose.prod.yaml up -d scraper
```

### 7.2 **Set Up Scheduled Scraping**

```bash
# Create scraping script
cat > /opt/phygitals/run_scraper.sh << 'EOF'
#!/bin/bash
cd /opt/phygitals
docker-compose -f docker-compose.prod.yaml run --rm scraper python scraper.py
EOF

chmod +x /opt/phygitals/run_scraper.sh

# Add to crontab for regular scraping (every 6 hours)
(crontab -l 2>/dev/null; echo "0 */6 * * * /opt/phygitals/run_scraper.sh") | crontab -
```

## 🌐 **Step 8: Access Your Application**

### 8.1 **Web Application**

- **URL**: `http://your-ec2-public-ip`
- **Features**: Data filtering, price history charts, search

### 8.2 **Database Access**

```bash
# Connect to database
docker exec -it phygitals-mysql mysql -u root -p

# Or from external client
mysql -h your-ec2-public-ip -u root -p -P 3306
```

## 🔧 **Step 9: Maintenance Commands**

### 9.1 **Common Operations**

```bash
# Check service status
docker-compose -f docker-compose.prod.yaml ps

# View logs
docker-compose -f docker-compose.prod.yaml logs -f webapp
docker-compose -f docker-compose.prod.yaml logs -f database

# Restart services
docker-compose -f docker-compose.prod.yaml restart

# Update application
git pull
docker-compose -f docker-compose.prod.yaml build
docker-compose -f docker-compose.prod.yaml up -d

# Check system resources
/opt/phygitals/monitor.sh

# Run backup
/opt/phygitals/backup.sh
```

### 9.2 **Troubleshooting**

```bash
# Check container health
docker ps -a

# Check container logs
docker logs phygitals-webapp
docker logs phygitals-mysql

# Check system resources
htop
df -h
free -h

# Check network connectivity
curl -I http://localhost:5001
```

## 💰 **Step 10: Cost Optimization**

### 10.1 **Instance Optimization**

- **Use Spot Instances** for non-critical workloads
- **Right-size instances** based on actual usage
- **Enable CloudWatch** for monitoring
- **Set up billing alerts**

### 10.2 **Storage Optimization**

- **Use EBS gp3** for better price/performance
- **Enable EBS encryption**
- **Set up lifecycle policies** for backups

## 📈 **Step 11: Scaling Considerations**

### 11.1 **Horizontal Scaling**

- **Load Balancer**: Use Application Load Balancer
- **Auto Scaling**: Set up Auto Scaling Groups
- **Database**: Consider RDS for managed MySQL

### 11.2 **Vertical Scaling**

- **Monitor performance** with CloudWatch
- **Upgrade instance type** as needed
- **Optimize Docker images** for size

## 🎉 **Success!**

Your Phygitals scraper is now deployed on AWS EC2 with:

- ✅ **Web Application** accessible at `http://your-ec2-ip`
- ✅ **MySQL Database** with persistent storage
- ✅ **Automated Scraping** with cron jobs
- ✅ **Backup System** for data protection
- ✅ **Monitoring** and logging
- ✅ **Security** configurations

## 🔗 **Next Steps**

1. **Set up a domain name** and configure DNS
2. **Implement SSL certificates** for HTTPS
3. **Set up CloudWatch** for advanced monitoring
4. **Configure RDS** for managed database
5. **Implement CI/CD** for automated deployments

## 📞 **Support**

If you encounter any issues:

1. Check the logs: `docker-compose logs -f`
2. Verify security group settings
3. Check system resources: `htop`
4. Review the troubleshooting section above

Your Phygitals scraper is now ready for production use on AWS EC2! 🚀
