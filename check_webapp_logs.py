#!/usr/bin/env python3
"""
Check webapp logs and fix the empty response issue
"""

import subprocess
import sys
import os
import time
import requests
from datetime import datetime

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_webapp_logs():
    """Check webapp container logs"""
    print("🔍 Checking Web App Logs...")
    print("-" * 30)
    
    success, stdout, stderr = run_command("docker logs phygitals-webapp")
    
    if success:
        print("📋 Web App Logs:")
        print(stdout)
        
        # Look for common error patterns
        if "Error" in stdout or "Exception" in stdout:
            print("\n❌ Errors found in logs!")
            return False
        elif "Running on" in stdout:
            print("\n✅ Web app appears to be running")
            return True
        else:
            print("\n⚠️  Logs don't show clear status")
            return False
    else:
        print(f"❌ Error getting logs: {stderr}")
        return False

def check_database_logs():
    """Check database container logs"""
    print("\n🗄️  Checking Database Logs...")
    print("-" * 30)
    
    success, stdout, stderr = run_command("docker logs phygitals-database")
    
    if success:
        print("📋 Database Logs:")
        print(stdout)
        
        # Look for ready message
        if "ready for connections" in stdout:
            print("\n✅ Database is ready")
            return True
        else:
            print("\n⚠️  Database may not be ready yet")
            return False
    else:
        print(f"❌ Error getting database logs: {stderr}")
        return False

def test_webapp_endpoints():
    """Test webapp endpoints"""
    print("\n🌐 Testing Web App Endpoints...")
    print("-" * 35)
    
    endpoints = [
        "http://127.0.0.1:5001/debug",
        "http://127.0.0.1:5001/",
        "http://localhost:5001/debug",
        "http://localhost:5001/"
    ]
    
    for url in endpoints:
        try:
            print(f"Testing {url}...")
            response = requests.get(url, timeout=5)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ {url} - Working")
                return True
            else:
                print(f"  ❌ {url} - Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {url} - Error: {e}")
    
    return False

def restart_webapp():
    """Restart the webapp container"""
    print("\n🔄 Restarting Web App Container...")
    print("-" * 35)
    
    # Stop webapp
    print("Stopping webapp...")
    run_command("docker stop phygitals-webapp")
    
    # Remove webapp
    print("Removing webapp...")
    run_command("docker rm phygitals-webapp")
    
    # Start webapp again
    print("Starting webapp...")
    success, stdout, stderr = run_command("docker-compose up -d webapp")
    
    if success:
        print("✅ Webapp restarted")
        print("⏳ Waiting for webapp to start...")
        time.sleep(10)
        return True
    else:
        print(f"❌ Error restarting webapp: {stderr}")
        return False

def fix_webapp_issue():
    """Try to fix the webapp issue"""
    print("\n🔧 Attempting to Fix Web App Issue...")
    print("-" * 40)
    
    # Check if the issue is with the template
    if os.path.exists("templates/index.html"):
        print("✅ Template file exists")
    else:
        print("❌ Template file missing!")
        return False
    
    # Check if the issue is with database connection
    print("Testing database connection...")
    success, stdout, stderr = run_command("docker exec phygitals-database mysql -u root -pmy-secret-pw -e 'SELECT 1'")
    
    if success:
        print("✅ Database connection working")
    else:
        print("❌ Database connection issue")
        print("This might be causing the webapp to crash")
    
    return True

def main():
    """Main diagnostic function"""
    print("🔍 Web App Diagnostic Tool")
    print("=" * 40)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check logs
    webapp_logs_ok = check_webapp_logs()
    database_logs_ok = check_database_logs()
    
    # Test endpoints
    endpoints_ok = test_webapp_endpoints()
    
    # Try to fix
    if not endpoints_ok:
        fix_webapp_issue()
        
        # Try restarting webapp
        print("\n🔄 Trying to restart webapp...")
        restart_success = restart_webapp()
        
        if restart_success:
            print("⏳ Waiting for restart...")
            time.sleep(15)
            
            # Test again
            endpoints_ok = test_webapp_endpoints()
    
    print("\n" + "=" * 40)
    print("📊 Diagnostic Results:")
    print(f"  Web App Logs: {'✅ OK' if webapp_logs_ok else '❌ ISSUES'}")
    print(f"  Database Logs: {'✅ OK' if database_logs_ok else '❌ ISSUES'}")
    print(f"  Endpoints: {'✅ WORKING' if endpoints_ok else '❌ NOT WORKING'}")
    
    if endpoints_ok:
        print("\n🎉 Web app is working!")
        print("🌐 Visit: http://localhost:5001")
    else:
        print("\n❌ Web app still not working")
        print("💡 Try running without Docker:")
        print("   python app_fixed.py")
    
    return endpoints_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
