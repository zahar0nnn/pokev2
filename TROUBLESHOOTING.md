# 🐳 Docker Troubleshooting Guide

## ERR_CONNECTION_REFUSED - Step by Step Solutions

### Step 1: Check if Docker is Running
```bash
# Check Docker version
docker --version

# Check if Docker daemon is running
docker info
```

**If Docker is not running:**
- Start Docker Desktop
- Wait for it to fully start (green status indicator)
- Try again

### Step 2: Check Container Status
```bash
# See all containers
docker ps -a

# Look for these containers:
# - phygitals-webapp
# - phygitals-database
# - phygitals-scraper
```

**If containers are not running:**
```bash
# Start all services
docker-compose up -d

# Wait 60 seconds for services to initialize
```

### Step 3: Check Container Logs
```bash
# Check webapp logs
docker logs phygitals-webapp

# Check database logs
docker logs phygitals-database

# Check scraper logs
docker logs phygitals-scraper
```

**Look for these error messages:**
- `Error connecting to MySQL`
- `Port already in use`
- `Container exited with code 1`

### Step 4: Test Web App Directly (Without Docker)
```bash
# Run this to test if the web app works at all
python test_webapp_direct.py
```

**If this works:**
- The web app is fine, issue is with Docker
- Try the Docker solutions below

**If this doesn't work:**
- Fix the web app first
- Check database connection
- Check Python dependencies

### Step 5: Restart Docker Services
```bash
# Stop all services
docker-compose down

# Remove containers and volumes (if needed)
docker-compose down -v

# Start fresh
docker-compose up -d

# Wait 60 seconds
```

### Step 6: Check Port Conflicts
```bash
# Check if port 5001 is already in use
netstat -an | findstr :5001

# If port is in use, kill the process or change port
```

### Step 7: Verify Database Connection
```bash
# Check if database is ready
docker exec -it phygitals-database mysql -u root -p

# Password: my-secret-pw
# Look for "ready for connections" message
```

### Step 8: Check Docker Compose Configuration
```bash
# Validate docker-compose.yaml
docker-compose config

# Check if all services are defined correctly
```

## Common Issues & Solutions

### Issue 1: "Container exited with code 1"
**Cause:** Web app crashed during startup
**Solution:**
```bash
# Check logs
docker logs phygitals-webapp

# Common fixes:
# - Database not ready (wait longer)
# - Missing dependencies (rebuild image)
# - Port conflicts (change port)
```

### Issue 2: "Error connecting to MySQL"
**Cause:** Database not ready or wrong credentials
**Solution:**
```bash
# Check database logs
docker logs phygitals-database

# Wait for "ready for connections" message
# Check environment variables in docker-compose.yaml
```

### Issue 3: "Port already in use"
**Cause:** Another service using port 5001
**Solution:**
```bash
# Find what's using port 5001
netstat -an | findstr :5001

# Kill the process or change port in docker-compose.yaml
```

### Issue 4: "Container not found"
**Cause:** Containers not created
**Solution:**
```bash
# Build and start
docker-compose up -d --build

# Or rebuild everything
docker-compose down
docker-compose up -d --build
```

## Quick Fix Commands

### Complete Reset
```bash
# Stop everything
docker-compose down -v

# Remove all containers
docker system prune -a

# Start fresh
docker-compose up -d --build

# Wait 60 seconds
# Visit: http://localhost:5001
```

### Check Everything
```bash
# Run diagnostic
python simple_docker_check.py

# Test web app directly
python test_webapp_direct.py

# Check Docker status
docker ps
docker logs phygitals-webapp
```

## Expected URLs
- ✅ http://localhost:5001
- ✅ http://127.0.0.1:5001
- ❌ http://localhost:5000 (wrong port)

## Still Not Working?

1. **Check Windows Firewall** - Allow Python and Docker through firewall
2. **Check Antivirus** - Some antivirus software blocks Docker
3. **Check Docker Desktop** - Make sure it's fully started
4. **Check System Resources** - Docker needs enough RAM/CPU
5. **Try Different Port** - Change port 5001 to 8080 in docker-compose.yaml

## Manual Testing
If Docker still doesn't work, you can run the web app directly:
```bash
# Install dependencies
pip install -r requirements.txt

# Start MySQL (or use Docker just for database)
docker run -d --name mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw -e MYSQL_DATABASE=scraped_data -p 3306:3306 mysql:8.0

# Run web app
python app.py

# Visit: http://localhost:5001
```
