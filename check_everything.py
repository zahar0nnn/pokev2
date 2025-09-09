#!/usr/bin/env python3
"""
Check everything - Docker, Python, files, etc.
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime

def check_python():
    """Check Python installation"""
    print("🐍 Checking Python...")
    print("-" * 25)
    
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check if we can import required modules
    try:
        import requests
        print("✅ requests module available")
    except ImportError:
        print("❌ requests module missing")
    
    try:
        import flask
        print("✅ flask module available")
    except ImportError:
        print("❌ flask module missing")
    
    try:
        import mysql.connector
        print("✅ mysql-connector module available")
    except ImportError:
        print("❌ mysql-connector module missing")
    
    return True

def check_docker():
    """Check Docker installation"""
    print("\n🐳 Checking Docker...")
    print("-" * 25)
    
    # Check if docker command exists
    docker_path = shutil.which('docker')
    if docker_path:
        print(f"✅ Docker found at: {docker_path}")
        
        # Try to run docker --version
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Docker version: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ Docker error: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Docker error: {e}")
            return False
    else:
        print("❌ Docker not found in PATH")
        print("💡 Install Docker Desktop from: https://www.docker.com/products/docker-desktop")
        return False

def check_files():
    """Check required files"""
    print("\n📁 Checking Files...")
    print("-" * 25)
    
    required_files = [
        "app.py",
        "scraper.py", 
        "database_config.py",
        "docker-compose.yaml",
        "Dockerfile.webapp",
        "requirements.txt",
        "templates/index.html"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_exist = False
    
    return all_exist

def check_ports():
    """Check if ports are available"""
    print("\n🔌 Checking Ports...")
    print("-" * 25)
    
    import socket
    
    ports_to_check = [5001, 3306]
    
    for port in ports_to_check:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print(f"⚠️  Port {port} is in use")
            else:
                print(f"✅ Port {port} is available")
        except Exception as e:
            print(f"❌ Error checking port {port}: {e}")

def check_webapp_direct():
    """Check if webapp can run directly"""
    print("\n🌐 Testing Web App Directly...")
    print("-" * 35)
    
    try:
        # Try to import the app
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app import app
        print("✅ Web app can be imported")
        
        # Check app configuration
        if hasattr(app, 'config'):
            print("✅ Flask app configured")
        
        return True
    except Exception as e:
        print(f"❌ Web app import error: {e}")
        return False

def provide_solutions():
    """Provide solutions based on what we found"""
    print("\n💡 Solutions:")
    print("-" * 15)
    
    print("1. 🐳 If Docker is not installed:")
    print("   - Download Docker Desktop from: https://www.docker.com/products/docker-desktop")
    print("   - Install and start Docker Desktop")
    print("   - Wait for green status indicator")
    
    print("\n2. 🐍 If Python modules are missing:")
    print("   - Run: pip install -r requirements.txt")
    
    print("\n3. 🌐 If you want to run without Docker:")
    print("   - Start MySQL manually or with Docker")
    print("   - Run: python app.py")
    print("   - Visit: http://localhost:5001")
    
    print("\n4. 🐳 If Docker is installed but not working:")
    print("   - Restart Docker Desktop")
    print("   - Run: docker-compose up -d")
    print("   - Wait 60 seconds")
    print("   - Visit: http://localhost:5001")

def main():
    """Main check function"""
    print("🔍 Complete System Check")
    print("=" * 40)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all checks
    python_ok = check_python()
    docker_ok = check_docker()
    files_ok = check_files()
    check_ports()
    webapp_ok = check_webapp_direct()
    
    # Provide solutions
    provide_solutions()
    
    print("\n" + "=" * 40)
    print("📊 Check Results:")
    print(f"  Python: {'✅ OK' if python_ok else '❌ ISSUES'}")
    print(f"  Docker: {'✅ OK' if docker_ok else '❌ NOT INSTALLED'}")
    print(f"  Files: {'✅ OK' if files_ok else '❌ MISSING'}")
    print(f"  Web App: {'✅ OK' if webapp_ok else '❌ ISSUES'}")
    
    if not docker_ok:
        print("\n❌ Docker is not installed!")
        print("💡 Install Docker Desktop first, then try again")
        print("💡 Or run the web app directly without Docker")
    elif files_ok and webapp_ok:
        print("\n✅ Everything looks good!")
        print("💡 Try running: docker-compose up -d")
    else:
        print("\n⚠️  Some issues found")
        print("💡 Fix the issues above first")
    
    return docker_ok and files_ok and webapp_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
