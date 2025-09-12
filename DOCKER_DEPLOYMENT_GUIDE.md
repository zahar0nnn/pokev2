# 🐳 Docker Deployment Guide

## ✅ **Current Status: Successfully Deployed!**

Your updated Phygitals scraper with all bug fixes has been successfully built and deployed to Docker.

## 📊 **Deployment Summary:**

### **Images Built:**
- ✅ `pokev2-scraper:latest` (633MB) - Updated scraper with bug fixes
- ✅ `pokev2-webapp:latest` (656MB) - Updated webapp with bug fixes
- ✅ `mysql:8.0` (1.07GB) - Database container

### **Containers Running:**
- ✅ `phygitals-mysql` - Database (Healthy)
- ✅ `phygitals-webapp` - Web application (Running on port 5001)
- ✅ `phygitals-scraper` - Scraper (Running)

## 🚀 **How to Deploy to Production:**

### **Option 1: Local Docker Deployment**
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f webapp
docker-compose logs -f scraper

# Stop services
docker-compose down
```

### **Option 2: Deploy to Remote Server**

#### **Step 1: Push to Docker Hub (if you have an account)**
```bash
# Tag images for Docker Hub
docker tag pokev2-scraper:latest yourusername/phygitals-scraper:latest
docker tag pokev2-webapp:latest yourusername/phygitals-webapp:latest

# Push to Docker Hub
docker push yourusername/phygitals-scraper:latest
docker push yourusername/phygitals-webapp:latest
```

#### **Step 2: Deploy to Remote Server**
```bash
# On your remote server, create a directory
mkdir phygitals-deployment
cd phygitals-deployment

# Copy docker-compose.yaml to server
# Then run:
docker-compose pull  # If using Docker Hub
docker-compose up -d
```

### **Option 3: Export/Import Images**
```bash
# Export images
docker save pokev2-scraper:latest > phygitals-scraper.tar
docker save pokev2-webapp:latest > phygitals-webapp.tar

# Transfer to remote server, then:
docker load < phygitals-scraper.tar
docker load < phygitals-webapp.tar
```

## 🔧 **Configuration:**

### **Environment Variables:**
The containers use these environment variables:
- `MYSQL_HOST`: Database host (default: database)
- `MYSQL_PORT`: Database port (default: 3306)
- `MYSQL_USER`: Database user (default: root)
- `MYSQL_PASSWORD`: Database password (default: my-secret-pw)
- `MYSQL_DATABASE`: Database name (default: scraped_data)

### **Ports:**
- **Webapp**: `5001` (http://localhost:5001)
- **Database**: `3306` (for external connections)

### **Volumes:**
- **Database Data**: `mysql_data` (persistent storage)
- **Scraper Data**: `./data` (local data directory)

## 🐛 **Bug Fixes Included:**

### **1. Database Schema Migration**
- ✅ Automatic `date` column addition
- ✅ Index creation for performance
- ✅ Backward compatibility with existing data

### **2. Price History Fixes**
- ✅ Fixed "No price history found" issue
- ✅ Items with zero prices now show in charts
- ✅ Better error messages

### **3. Data Extraction Consistency**
- ✅ Unified field structure across all functions
- ✅ Date-based ordering implemented
- ✅ Consistent data format

### **4. Price Calculation Improvements**
- ✅ Better edge case handling
- ✅ Robust amount-to-price conversion
- ✅ Improved error handling

## 📋 **Testing Your Deployment:**

### **1. Check Web Application**
```bash
# Open in browser
http://localhost:5001

# Or test with curl
curl http://localhost:5001/debug
```

### **2. Check Database Connection**
```bash
# Connect to database
docker exec -it phygitals-mysql mysql -u root -pmy-secret-pw scraped_data

# Check tables
SHOW TABLES;
DESCRIBE transactions;
```

### **3. Check Scraper Logs**
```bash
# View scraper logs
docker logs phygitals-scraper

# Follow logs in real-time
docker logs -f phygitals-scraper
```

## 🔄 **Updating Deployment:**

### **When you make changes:**
```bash
# 1. Commit changes
git add .
git commit -m "Your changes"

# 2. Rebuild images
docker-compose build

# 3. Restart services
docker-compose down
docker-compose up -d
```

### **For production updates:**
```bash
# 1. Pull latest changes
git pull

# 2. Rebuild and restart
docker-compose build
docker-compose down
docker-compose up -d
```

## 🛠️ **Troubleshooting:**

### **Common Issues:**

#### **1. Port Already in Use**
```bash
# Check what's using port 5001
netstat -ano | findstr :5001

# Kill the process or change port in docker-compose.yaml
```

#### **2. Database Connection Issues**
```bash
# Check database logs
docker logs phygitals-mysql

# Restart database
docker-compose restart database
```

#### **3. Container Won't Start**
```bash
# Check logs
docker logs phygitals-webapp
docker logs phygitals-scraper

# Check container status
docker-compose ps
```

## 📊 **Monitoring:**

### **Health Checks:**
- **Database**: MySQL ping every 10s
- **Webapp**: HTTP check every 30s

### **Logs:**
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs webapp
docker-compose logs scraper
docker-compose logs database
```

## 🎉 **Success!**

Your Phygitals scraper is now successfully deployed with all bug fixes:

- ✅ **Database schema migration** - Handles both new and existing databases
- ✅ **Price history fixes** - No more "No price history found" issues
- ✅ **Data consistency** - Unified data structure across all functions
- ✅ **Price calculation** - Robust handling of edge cases
- ✅ **Docker deployment** - Ready for production use

The web application is accessible at **http://localhost:5001** and all services are running properly!
