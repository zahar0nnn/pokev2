#!/usr/bin/env python3
"""
Docker diagnostic script to check container status and fix issues.
"""

import subprocess
import sys
import time
import requests
from datetime import datetime

def run_docker_command(command):
    """Run a docker command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_docker_installed():
    """Check if Docker is installed and running"""
    print("🐳 Checking Docker Installation...")
    print("-" * 35)
    
    success, stdout, stderr = run_docker_command("docker --version")
    if success:
        print(f"✅ Docker installed: {stdout.strip()}")
    else:
        print(f"❌ Docker not found: {stderr}")
        return False
    
    success, stdout, stderr = run_docker_command("docker info")
    if success:
        print("✅ Docker daemon is running")
        return True
    else:
        print(f"❌ Docker daemon not running: {stderr}")
        return False

def check_containers():
    """Check container status"""
    print("\n📦 Checking Container Status...")
    print("-" * 35)
    
    success, stdout, stderr = run_docker_command("docker ps -a")
    if not success:
        print(f"❌ Error checking containers: {stderr}")
        return False
    
    containers = stdout.strip().split('\n')[1:]  # Skip header
    running_containers = []
    
    for container in containers:
        if container.strip():
            parts = container.split()
            if len(parts) >= 2:
                container_id = parts[0]
                status = parts[4] if len(parts) > 4 else "unknown"
                name = parts[-1] if len(parts) > 1 else "unknown"
                
                if "Up" in status:
                    running_containers.append(name)
                    print(f"✅ {name}: {status}")
                else:
                    print(f"❌ {name}: {status}")
    
    return running_containers

def check_webapp_access():
    """Check if webapp is accessible"""
    print("\n🌐 Checking Web App Access...")
    print("-" * 35)
    
    urls = [
        "http://localhost:5001",
        "http://127.0.0.1:5001"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Web app accessible at {url}")
                return True
        except requests.exceptions.RequestException as e:
            print(f"❌ {url}: {e}")
    
    return False

def start_docker_services():
    """Start Docker services"""
    print("\n🚀 Starting Docker Services...")
    print("-" * 35)
    
    # Check if docker-compose.yaml exists
    import os
    if not os.path.exists("docker-compose.yaml"):
        print("❌ docker-compose.yaml not found")
        return False
    
    print("✅ docker-compose.yaml found")
    
    # Start services
    success, stdout, stderr = run_docker_command("docker-compose up -d")
    if success:
        print("✅ Docker services started")
        print("⏳ Waiting for services to initialize...")
        time.sleep(10)  # Wait for services to start
        return True
    else:
        print(f"❌ Error starting services: {stderr}")
        return False

def check_logs():
    """Check container logs for errors"""
    print("\n📋 Checking Container Logs...")
    print("-" * 35)
    
    containers = ["phygitals-webapp", "phygitals-database", "phygitals-scraper"]
    
    for container in containers:
        print(f"\n🔍 {container} logs:")
        success, stdout, stderr = run_docker_command(f"docker logs {container} --tail 10")
        if success:
            if stdout.strip():
                print(stdout)
            else:
                print("  (no recent logs)")
        else:
            print(f"  Error: {stderr}")

def provide_solutions():
    """Provide solutions for Docker issues"""
    print("\n💡 Solutions for Docker Issues:")
    print("-" * 35)
    
    print("1. 🚀 Start Docker services:")
    print("   docker-compose up -d")
    
    print("\n2. 🔍 Check container status:")
    print("   docker ps")
    
    print("\n3. 📋 Check logs for errors:")
    print("   docker logs phygitals-webapp")
    print("   docker logs phygitals-database")
    
    print("\n4. 🔄 Restart services:")
    print("   docker-compose down")
    print("   docker-compose up -d")
    
    print("\n5. 🌐 Access the web app:")
    print("   http://localhost:5001")
    print("   http://127.0.0.1:5001")
    
    print("\n6. 🗄️  Check database connection:")
    print("   docker exec -it phygitals-database mysql -u root -p")

def main():
    """Main diagnostic function"""
    print("🐳 Docker Diagnostic Tool")
    print("=" * 40)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check Docker installation
    docker_ok = check_docker_installed()
    if not docker_ok:
        print("\n❌ Docker is not installed or not running")
        print("💡 Please install Docker Desktop and start it")
        return False
    
    # Check containers
    running_containers = check_containers()
    
    # Check web app access
    webapp_accessible = check_webapp_access()
    
    # If webapp not accessible, try to start services
    if not webapp_accessible:
        print("\n🔄 Web app not accessible, trying to start services...")
        start_success = start_docker_services()
        
        if start_success:
            # Check again after starting
            time.sleep(5)
            webapp_accessible = check_webapp_access()
    
    # Check logs if there are issues
    if not webapp_accessible:
        check_logs()
    
    # Provide solutions
    provide_solutions()
    
    print("\n" + "=" * 40)
    print("📊 Diagnostic Results:")
    print(f"  Docker: {'✅ WORKING' if docker_ok else '❌ NOT WORKING'}")
    print(f"  Containers: {len(running_containers)} running")
    print(f"  Web App: {'✅ ACCESSIBLE' if webapp_accessible else '❌ NOT ACCESSIBLE'}")
    
    if webapp_accessible:
        print("\n🎉 Web app is working!")
        print("🌐 Visit: http://localhost:5001")
    else:
        print("\n❌ Web app is not accessible")
        print("💡 Check the solutions above")
    
    return webapp_accessible

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
