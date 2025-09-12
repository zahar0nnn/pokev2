# 🔍 Scraper Monitoring Guide for EC2

This guide provides multiple methods to check if your Phygitals scraper is still working on your EC2 instance.

## 🚀 **Quick Status Check (1 minute)**

### Method 1: Simple Commands
```bash
# SSH into your EC2 instance
ssh -i "your-key.pem" ubuntu@your-ec2-ip-address

# Check if containers are running
docker ps

# Check scraper logs (last 20 lines)
docker logs --tail 20 phygitals-scraper

# Check progress file
cat scraping_progress.json
```

### Method 2: Use the Monitoring Script
```bash
# Run the comprehensive monitoring script
python3 monitor_scraper.py

# Or use the quick shell script
./check_scraper.sh
```

## 📊 **Detailed Monitoring Methods**

### 1. **Docker Container Status**
```bash
# Check all containers
docker ps -a

# Check specific scraper container
docker ps | grep scraper

# Check container health
docker inspect phygitals-scraper | grep -A 5 "Health"
```

### 2. **Scraper Logs Analysis**
```bash
# View recent logs
docker logs --tail 50 phygitals-scraper

# Follow logs in real-time
docker logs -f phygitals-scraper

# Check for errors
docker logs phygitals-scraper 2>&1 | grep -i error

# Check for recent activity
docker logs phygitals-scraper 2>&1 | grep -i "scraping\|batch\|progress"
```

### 3. **Progress File Monitoring**
```bash
# Check if progress file exists
ls -la scraping_progress.json

# View current progress
cat scraping_progress.json | jq '.'

# Check when last updated
stat scraping_progress.json

# Monitor progress in real-time
watch -n 30 'cat scraping_progress.json | jq .'
```

### 4. **Database Activity Check**
```bash
# Connect to database
docker exec -it phygitals-mysql mysql -u root -p

# Check total records
USE scraped_data;
SELECT COUNT(*) as total_records FROM transactions;

# Check recent activity (last hour)
SELECT COUNT(*) as recent_records FROM transactions 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR);

# Check latest record
SELECT MAX(created_at) as latest_record FROM transactions;

# Check records by day (last 7 days)
SELECT DATE(created_at) as date, COUNT(*) as records 
FROM transactions 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### 5. **System Resource Monitoring**
```bash
# Check memory usage
free -h

# Check disk usage
df -h

# Check CPU usage
htop

# Check Docker stats
docker stats --no-stream

# Check system load
uptime
```

### 6. **Web App Status**
```bash
# Test web app locally
curl -I http://localhost:5001/debug

# Test from external IP
curl -I http://your-ec2-public-ip/debug

# Check web app logs
docker logs phygitals-webapp
```

## 🔧 **Troubleshooting Common Issues**

### Issue 1: Scraper Container Not Running
```bash
# Check if container exists
docker ps -a | grep scraper

# Start scraper manually
docker-compose -f docker-compose.prod.yaml run scraper python scraper.py

# Or start in background
docker-compose -f docker-compose.prod.yaml up -d scraper
```

### Issue 2: No Recent Activity
```bash
# Check if scraper is stuck
docker logs phygitals-scraper | tail -50

# Restart scraper
docker restart phygitals-scraper

# Or recreate scraper
docker-compose -f docker-compose.prod.yaml down scraper
docker-compose -f docker-compose.prod.yaml up -d scraper
```

### Issue 3: Database Connection Issues
```bash
# Check database status
docker logs phygitals-mysql

# Test database connection
docker exec phygitals-mysql mysql -u root -p -e "SELECT 1"

# Restart database
docker restart phygitals-mysql
```

### Issue 4: Web App Not Accessible
```bash
# Check web app logs
docker logs phygitals-webapp

# Check if port is open
netstat -tlnp | grep :5001

# Restart web app
docker restart phygitals-webapp
```

## 📈 **Automated Monitoring Setup**

### 1. **Set Up Cron Job for Regular Checks**
```bash
# Edit crontab
crontab -e

# Add this line to check every 30 minutes
*/30 * * * * /opt/phygitals/check_scraper.sh >> /opt/phygitals/monitor.log 2>&1

# Or check every hour
0 * * * * /opt/phygitals/check_scraper.sh >> /opt/phygitals/monitor.log 2>&1
```

### 2. **Set Up Log Rotation**
```bash
# Create logrotate config
sudo nano /etc/logrotate.d/phygitals-monitor

# Add this content:
/opt/phygitals/monitor.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 ubuntu ubuntu
}
```

### 3. **Set Up Alerts (Optional)**
```bash
# Create alert script
cat > /opt/phygitals/alert_check.sh << 'EOF'
#!/bin/bash
if ! python3 /opt/phygitals/monitor_scraper.py; then
    echo "Scraper issue detected at $(date)" | mail -s "Scraper Alert" your-email@example.com
fi
EOF

chmod +x /opt/phygitals/alert_check.sh
```

## 🎯 **Quick Health Check Commands**

### One-liner Status Check
```bash
echo "=== Scraper Status ===" && \
docker ps | grep scraper && \
echo "=== Recent Logs ===" && \
docker logs --tail 5 phygitals-scraper && \
echo "=== Progress ===" && \
cat scraping_progress.json 2>/dev/null | jq '.progress_percentage' && \
echo "=== Database ===" && \
docker exec phygitals-mysql mysql -u root -p${MYSQL_ROOT_PASSWORD} -e "SELECT COUNT(*) FROM scraped_data.transactions" 2>/dev/null
```

### System Health Check
```bash
echo "=== System Resources ===" && \
free -h | head -2 && \
echo "=== Disk Usage ===" && \
df -h | grep -E "(Filesystem|/dev/)" && \
echo "=== Docker Stats ===" && \
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

## 📱 **Monitoring Dashboard Commands**

### Real-time Monitoring
```bash
# Watch scraper logs
watch -n 5 'docker logs --tail 10 phygitals-scraper'

# Watch progress
watch -n 30 'cat scraping_progress.json | jq .'

# Watch system resources
watch -n 10 'htop'

# Watch Docker stats
watch -n 5 'docker stats --no-stream'
```

## 🚨 **Emergency Recovery**

### If Scraper Completely Stops
```bash
# 1. Check what's wrong
docker logs phygitals-scraper

# 2. Restart all services
docker-compose -f docker-compose.prod.yaml down
docker-compose -f docker-compose.prod.yaml up -d

# 3. Start scraper manually
docker-compose -f docker-compose.prod.yaml run scraper python scraper.py

# 4. Check if it's working
python3 monitor_scraper.py
```

### If Database Issues
```bash
# 1. Check database logs
docker logs phygitals-mysql

# 2. Restart database
docker restart phygitals-mysql

# 3. Wait for database to be ready
sleep 30

# 4. Test connection
docker exec phygitals-mysql mysql -u root -p -e "SELECT 1"
```

## 📊 **Performance Monitoring**

### Check Scraping Speed
```bash
# Count records per hour
docker exec phygitals-mysql mysql -u root -p -e "
SELECT 
    HOUR(created_at) as hour,
    COUNT(*) as records
FROM scraped_data.transactions 
WHERE DATE(created_at) = CURDATE()
GROUP BY HOUR(created_at)
ORDER BY hour;
"
```

### Check Memory Usage
```bash
# Monitor scraper memory usage
docker stats phygitals-scraper --no-stream --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}"
```

## 🎉 **Success Indicators**

Your scraper is working properly if you see:

✅ **Docker containers running**: `docker ps` shows phygitals-scraper as "Up"  
✅ **Recent logs**: `docker logs phygitals-scraper` shows recent scraping activity  
✅ **Progress file updated**: `scraping_progress.json` has recent timestamp  
✅ **Database activity**: New records being added to transactions table  
✅ **Web app accessible**: `curl http://localhost:5001/debug` returns 200  
✅ **System resources stable**: No memory leaks or high CPU usage  

## 📞 **Need Help?**

If you're still having issues:

1. **Check the logs**: `docker logs phygitals-scraper`
2. **Run diagnostics**: `python3 monitor_scraper.py`
3. **Check system resources**: `htop` and `df -h`
4. **Verify network**: `curl -I https://api.phygitals.com/api/marketplace/sales`
5. **Restart services**: `docker-compose -f docker-compose.prod.yaml restart`

Your scraper should now be fully monitored and maintainable! 🚀
