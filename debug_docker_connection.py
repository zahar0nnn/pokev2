#!/usr/bin/env python3
"""
Debug Docker connection issues
"""

import subprocess
import sys
import os
import time
import requests
import socket
from datetime import datetime

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_docker_status():
    """Check if Docker containers are running"""
    print("🐳 Checking Docker Container Status...")
    print("-" * 40)
    
    success, stdout, stderr = run_command("docker ps")
    
    if success:
        print("📋 Running Containers:")
        print(stdout)
        
        # Check for our specific containers
        if "phygitals-webapp" in stdout:
            print("✅ phygitals-webapp is running")
        else:
            print("❌ phygitals-webapp is NOT running")
        
        if "phygitals-database" in stdout:
            print("✅ phygitals-database is running")
        else:
            print("❌ phygitals-database is NOT running")
        
        return True
    else:
        print(f"❌ Error checking containers: {stderr}")
        return False

def check_port_binding():
    """Check if port 5001 is bound correctly"""
    print("\n🔌 Checking Port Binding...")
    print("-" * 30)
    
    success, stdout, stderr = run_command("docker ps --format 'table {{.Names}}\\t{{.Ports}}'")
    
    if success:
        print("📋 Port Mappings:")
        print(stdout)
        
        # Look for port 5001 mapping
        if "5001->5001" in stdout:
            print("✅ Port 5001 is mapped correctly")
            return True
        else:
            print("❌ Port 5001 is NOT mapped correctly")
            return False
    else:
        print(f"❌ Error checking ports: {stderr}")
        return False

def check_webapp_logs():
    """Check webapp container logs"""
    print("\n📋 Checking Web App Logs...")
    print("-" * 30)
    
    success, stdout, stderr = run_command("docker logs phygitals-webapp --tail 20")
    
    if success:
        print("📋 Recent Web App Logs:")
        print(stdout)
        
        # Look for key indicators
        if "Running on" in stdout:
            print("✅ Web app is running")
        elif "Error" in stdout or "Exception" in stdout:
            print("❌ Errors found in logs")
        else:
            print("⚠️  Logs don't show clear status")
        
        return True
    else:
        print(f"❌ Error getting logs: {stderr}")
        return False

def test_connection():
    """Test connection to the web app"""
    print("\n🌐 Testing Connection...")
    print("-" * 25)
    
    urls_to_test = [
        "http://127.0.0.1:5001",
        "http://localhost:5001",
        "http://0.0.0.0:5001"
    ]
    
    for url in urls_to_test:
        try:
            print(f"Testing {url}...")
            response = requests.get(url, timeout=5)
            print(f"  ✅ Status: {response.status_code}")
            return True
        except requests.exceptions.ConnectionError as e:
            print(f"  ❌ Connection refused: {e}")
        except requests.exceptions.Timeout as e:
            print(f"  ⏰ Timeout: {e}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    return False

def check_port_availability():
    """Check if port 5001 is available on the host"""
    print("\n🔍 Checking Port Availability...")
    print("-" * 35)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 5001))
        sock.close()
        
        if result == 0:
            print("✅ Port 5001 is accessible")
            return True
        else:
            print("❌ Port 5001 is not accessible")
            return False
    except Exception as e:
        print(f"❌ Error checking port: {e}")
        return False

def restart_containers():
    """Restart Docker containers"""
    print("\n🔄 Restarting Docker Containers...")
    print("-" * 35)
    
    # Stop containers
    print("Stopping containers...")
    run_command("docker-compose down")
    
    # Start containers
    print("Starting containers...")
    success, stdout, stderr = run_command("docker-compose up -d")
    
    if success:
        print("✅ Containers restarted")
        print("⏳ Waiting for services to initialize...")
        time.sleep(30)
        return True
    else:
        print(f"❌ Error restarting: {stderr}")
        return False

def provide_solutions():
    """Provide solutions based on findings"""
    print("\n💡 Solutions:")
    print("-" * 15)
    
    print("1. 🔄 Restart Docker Desktop:")
    print("   - Close Docker Desktop")
    print("   - Wait 10 seconds")
    print("   - Start Docker Desktop again")
    print("   - Wait for green status")
    
    print("\n2. 🐳 Restart containers:")
    print("   docker-compose down")
    print("   docker-compose up -d")
    
    print("\n3. 🔧 Rebuild containers:")
    print("   docker-compose down")
    print("   docker-compose up -d --build")
    
    print("\n4. 🌐 Try different URLs:")
    print("   - http://localhost:5001")
    print("   - http://127.0.0.1:5001")
    print("   - http://0.0.0.0:5001")
    
    print("\n5. 🔍 Check Windows Firewall:")
    print("   - Allow Python through firewall")
    print("   - Allow Docker through firewall")
    
    print("\n6. 🚀 Run without Docker:")
    print("   python app_fixed.py")
    print("   Then visit: http://localhost:5001")

def main():
    """Main diagnostic function"""
    print("🔍 Docker Connection Debug Tool")
    print("=" * 40)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all checks
    docker_ok = check_docker_status()
    ports_ok = check_port_binding()
    logs_ok = check_webapp_logs()
    connection_ok = test_connection()
    port_available = check_port_availability()
    
    # Provide solutions
    provide_solutions()
    
    print("\n" + "=" * 40)
    print("📊 Diagnostic Results:")
    print(f"  Docker Status: {'✅ OK' if docker_ok else '❌ ISSUES'}")
    print(f"  Port Binding: {'✅ OK' if ports_ok else '❌ ISSUES'}")
    print(f"  Web App Logs: {'✅ OK' if logs_ok else '❌ ISSUES'}")
    print(f"  Connection: {'✅ WORKING' if connection_ok else '❌ NOT WORKING'}")
    print(f"  Port Available: {'✅ YES' if port_available else '❌ NO'}")
    
    if not connection_ok:
        print("\n❌ Connection still not working")
        print("💡 Try the solutions above")
        print("💡 Or run without Docker: python app_fixed.py")
    else:
        print("\n🎉 Connection is working!")
        print("🌐 Visit: http://localhost:5001")
    
    return connection_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
