#!/usr/bin/env python3
"""
Script to recreate Docker containers
"""

import subprocess
import sys
import time
import os
from datetime import datetime

def run_command(command, description):
    """Run a command and return (success, stdout, stderr)"""
    print(f"🔄 {description}...")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return True, result.stdout, result.stderr
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False, "", "Command timed out"
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False, "", str(e)

def check_docker_installed():
    """Check if Docker is installed"""
    print("🐳 Checking Docker Installation...")
    print("-" * 35)
    
    # Check docker command
    success, stdout, stderr = run_command("docker --version", "Docker version check")
    if not success:
        print("❌ Docker not found!")
        print("💡 Please install Docker Desktop from: https://www.docker.com/products/docker-desktop")
        return False
    
    # Check docker-compose command
    success, stdout, stderr = run_command("docker-compose --version", "Docker Compose version check")
    if not success:
        print("❌ Docker Compose not found!")
        print("💡 Try using 'docker compose' instead of 'docker-compose'")
        return False
    
    return True

def recreate_containers():
    """Recreate Docker containers"""
    print("\n🚀 Recreating Docker Containers...")
    print("-" * 40)
    
    # Step 1: Stop any existing containers
    print("1️⃣ Stopping existing containers...")
    run_command("docker-compose down", "Stop containers")
    
    # Step 2: Remove old containers and images
    print("\n2️⃣ Cleaning up old containers...")
    run_command("docker-compose down -v", "Remove containers and volumes")
    run_command("docker system prune -f", "Clean up Docker system")
    
    # Step 3: Build and start new containers
    print("\n3️⃣ Building and starting new containers...")
    success, stdout, stderr = run_command("docker-compose up -d --build", "Build and start containers")
    
    if success:
        print("\n⏳ Waiting for services to initialize...")
        print("   This may take 1-2 minutes...")
        time.sleep(30)
        
        # Step 4: Check container status
        print("\n4️⃣ Checking container status...")
        run_command("docker ps", "Check running containers")
        
        # Step 5: Check logs
        print("\n5️⃣ Checking container logs...")
        run_command("docker logs phygitals-webapp", "Web app logs")
        run_command("docker logs phygitals-database", "Database logs")
        
        return True
    else:
        print("\n❌ Failed to create containers")
        return False

def provide_manual_commands():
    """Provide manual commands if script fails"""
    print("\n💡 Manual Commands (if script fails):")
    print("-" * 45)
    
    print("1. 🛑 Stop everything:")
    print("   docker-compose down -v")
    
    print("\n2. 🧹 Clean up:")
    print("   docker system prune -a")
    
    print("\n3. 🚀 Recreate containers:")
    print("   docker-compose up -d --build")
    
    print("\n4. ⏳ Wait 60 seconds, then check:")
    print("   docker ps")
    
    print("\n5. 🌐 Visit the web app:")
    print("   http://localhost:5001")
    
    print("\n6. 📋 Check logs if there are issues:")
    print("   docker logs phygitals-webapp")
    print("   docker logs phygitals-database")

def main():
    """Main function"""
    print("🐳 Docker Container Recreation Script")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if Docker is installed
    if not check_docker_installed():
        print("\n❌ Docker is not installed or not working")
        print("💡 Please install Docker Desktop first")
        return False
    
    # Check if docker-compose.yaml exists
    if not os.path.exists("docker-compose.yaml"):
        print("\n❌ docker-compose.yaml not found")
        print("💡 Make sure you're in the correct directory")
        return False
    
    print("✅ Docker and docker-compose.yaml found")
    
    # Recreate containers
    success = recreate_containers()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 DOCKER CONTAINERS RECREATED SUCCESSFULLY!")
        print("=" * 50)
        print("🌐 Web app should be available at:")
        print("   http://localhost:5001")
        print("   http://127.0.0.1:5001")
        print("\n💡 If you still get errors:")
        print("   - Wait 60 seconds for services to fully start")
        print("   - Check logs: docker logs phygitals-webapp")
        print("   - Try the manual commands above")
    else:
        print("\n" + "=" * 50)
        print("❌ FAILED TO RECREATE CONTAINERS")
        print("=" * 50)
        print("💡 Try the manual commands above")
        print("💡 Or run without Docker: python app_fixed.py")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
