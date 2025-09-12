#!/usr/bin/env python3
"""
Comprehensive scraper monitoring script for EC2 deployment
Checks scraper status, progress, database activity, and system health
"""

import subprocess
import json
import time
import requests
import os
from datetime import datetime, timedelta
from database_config import DatabaseConfig

def run_command(command, timeout=30):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_docker_containers():
    """Check if Docker containers are running"""
    print("🐳 Checking Docker Containers...")
    print("-" * 35)
    
    success, stdout, stderr = run_command("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'")
    
    if success:
        print(stdout)
        
        # Check for scraper container
        if "phygitals-scraper" in stdout:
            if "Up" in stdout:
                print("✅ Scraper container is running")
                return True
            else:
                print("⚠️  Scraper container exists but not running")
                return False
        else:
            print("❌ Scraper container not found")
            return False
    else:
        print(f"❌ Error checking containers: {stderr}")
        return False

def check_scraper_logs():
    """Check scraper container logs for recent activity"""
    print("\n📋 Checking Scraper Logs...")
    print("-" * 30)
    
    success, stdout, stderr = run_command("docker logs --tail 20 phygitals-scraper")
    
    if success:
        print("Recent scraper logs:")
        print(stdout)
        
        # Look for recent activity (last 10 minutes)
        current_time = datetime.now()
        recent_activity = False
        
        for line in stdout.split('\n'):
            if any(keyword in line.lower() for keyword in ['scraping', 'batch', 'progress', 'saved']):
                recent_activity = True
                break
        
        if recent_activity:
            print("✅ Recent scraper activity detected")
            return True
        else:
            print("⚠️  No recent scraper activity")
            return False
    else:
        print(f"❌ Error getting scraper logs: {stderr}")
        return False

def check_progress_file():
    """Check scraping progress file"""
    print("\n📊 Checking Progress File...")
    print("-" * 30)
    
    if not os.path.exists('scraping_progress.json'):
        print("❌ Progress file not found")
        return False
    
    try:
        with open('scraping_progress.json', 'r') as f:
            progress = json.load(f)
        
        print(f"📈 Progress: {progress.get('progress_percentage', 0)}%")
        print(f"📦 Batch: {progress.get('batch_number', 0)}/{progress.get('total_batches', 0)}")
        print(f"📊 Records: {progress.get('records_count', 0)}")
        print(f"⏰ Last Update: {progress.get('timestamp', 'Unknown')}")
        
        # Check if progress is recent (within last hour)
        try:
            last_update = datetime.fromisoformat(progress.get('timestamp', ''))
            if datetime.now() - last_update < timedelta(hours=1):
                print("✅ Progress file is recent")
                return True
            else:
                print("⚠️  Progress file is outdated")
                return False
        except:
            print("⚠️  Could not parse timestamp")
            return False
            
    except Exception as e:
        print(f"❌ Error reading progress file: {e}")
        return False

def check_database_activity():
    """Check database for recent activity"""
    print("\n🗄️  Checking Database Activity...")
    print("-" * 35)
    
    try:
        db = DatabaseConfig()
        connection = db.get_connection()
        cursor = connection.cursor()
        
        # Check total records
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total_records = cursor.fetchone()[0]
        print(f"📊 Total records: {total_records:,}")
        
        # Check recent records (last hour)
        cursor.execute("""
            SELECT COUNT(*) FROM transactions 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
        """)
        recent_records = cursor.fetchone()[0]
        print(f"🕐 Records in last hour: {recent_records:,}")
        
        # Check latest record
        cursor.execute("SELECT MAX(created_at) FROM transactions")
        latest_record = cursor.fetchone()[0]
        if latest_record:
            print(f"⏰ Latest record: {latest_record}")
            
            # Check if latest record is recent
            if datetime.now() - latest_record < timedelta(hours=2):
                print("✅ Recent database activity detected")
                return True
            else:
                print("⚠️  No recent database activity")
                return False
        else:
            print("❌ No records in database")
            return False
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

def check_system_resources():
    """Check system resource usage"""
    print("\n💻 Checking System Resources...")
    print("-" * 35)
    
    # Check memory usage
    success, stdout, stderr = run_command("free -h")
    if success:
        print("Memory usage:")
        print(stdout)
    
    # Check disk usage
    success, stdout, stderr = run_command("df -h")
    if success:
        print("\nDisk usage:")
        print(stdout)
    
    # Check Docker stats
    success, stdout, stderr = run_command("docker stats --no-stream --format 'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}'")
    if success:
        print("\nDocker container stats:")
        print(stdout)

def check_webapp_status():
    """Check if webapp is accessible"""
    print("\n🌐 Checking Web App Status...")
    print("-" * 35)
    
    try:
        response = requests.get("http://localhost:5001/debug", timeout=5)
        if response.status_code == 200:
            print("✅ Web app is accessible")
            return True
        else:
            print(f"⚠️  Web app returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Web app not accessible: {e}")
        return False

def restart_scraper():
    """Restart the scraper container"""
    print("\n🔄 Restarting Scraper...")
    print("-" * 30)
    
    # Stop scraper
    print("Stopping scraper...")
    run_command("docker stop phygitals-scraper")
    
    # Remove scraper
    print("Removing scraper...")
    run_command("docker rm phygitals-scraper")
    
    # Start scraper
    print("Starting scraper...")
    success, stdout, stderr = run_command("docker-compose -f docker-compose.prod.yaml run -d scraper python scraper.py")
    
    if success:
        print("✅ Scraper restarted")
        return True
    else:
        print(f"❌ Error restarting scraper: {stderr}")
        return False

def main():
    """Main monitoring function"""
    print("🔍 Phygitals Scraper Monitor")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check all components
    containers_ok = check_docker_containers()
    logs_ok = check_scraper_logs()
    progress_ok = check_progress_file()
    database_ok = check_database_activity()
    webapp_ok = check_webapp_status()
    
    # Check system resources
    check_system_resources()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Monitoring Summary:")
    print(f"  Docker Containers: {'✅ OK' if containers_ok else '❌ ISSUES'}")
    print(f"  Scraper Logs: {'✅ OK' if logs_ok else '❌ ISSUES'}")
    print(f"  Progress File: {'✅ OK' if progress_ok else '❌ ISSUES'}")
    print(f"  Database Activity: {'✅ OK' if database_ok else '❌ ISSUES'}")
    print(f"  Web App: {'✅ OK' if webapp_ok else '❌ ISSUES'}")
    
    # Overall status
    overall_ok = containers_ok and (logs_ok or progress_ok or database_ok)
    
    if overall_ok:
        print("\n🎉 Scraper appears to be working!")
    else:
        print("\n❌ Scraper may not be working properly")
        print("\n💡 Suggested actions:")
        if not containers_ok:
            print("  - Check Docker service: sudo systemctl status docker")
        if not logs_ok and not progress_ok and not database_ok:
            print("  - Restart scraper: docker-compose -f docker-compose.prod.yaml run scraper python scraper.py")
        if not webapp_ok:
            print("  - Check webapp: docker logs phygitals-webapp")
    
    return overall_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
