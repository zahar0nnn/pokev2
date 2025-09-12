#!/bin/bash
# Quick scraper status check script for EC2

echo "🔍 Phygitals Scraper Status Check"
echo "=================================="
echo "Time: $(date)"
echo

# Check Docker containers
echo "🐳 Docker Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo

# Check scraper logs (last 10 lines)
echo "📋 Recent Scraper Logs:"
docker logs --tail 10 phygitals-scraper 2>/dev/null || echo "❌ Scraper container not found or not running"
echo

# Check progress file
echo "📊 Scraping Progress:"
if [ -f "scraping_progress.json" ]; then
    cat scraping_progress.json | jq '.' 2>/dev/null || cat scraping_progress.json
    echo
    echo "📅 Last modified: $(stat -c %y scraping_progress.json 2>/dev/null || echo 'Unknown')"
else
    echo "❌ Progress file not found"
fi
echo

# Check database activity
echo "🗄️  Database Activity:"
docker exec phygitals-mysql mysql -u root -p${MYSQL_ROOT_PASSWORD:-your-secure-password-here} -e "
USE scraped_data;
SELECT 'Total Records:' as info, COUNT(*) as count FROM transactions
UNION ALL
SELECT 'Records Today:', COUNT(*) FROM transactions WHERE DATE(created_at) = CURDATE()
UNION ALL
SELECT 'Records Last Hour:', COUNT(*) FROM transactions WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
UNION ALL
SELECT 'Latest Record:', MAX(created_at) FROM transactions;
" 2>/dev/null || echo "❌ Database not accessible"
echo

# Check system resources
echo "💻 System Resources:"
echo "Memory:"
free -h | head -2
echo
echo "Disk:"
df -h | grep -E "(Filesystem|/dev/)"
echo

# Check webapp
echo "🌐 Web App Status:"
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:5001/debug || echo "❌ Web app not accessible"
echo

echo "=================================="
echo "✅ Check complete!"
