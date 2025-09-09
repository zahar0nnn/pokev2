#!/usr/bin/env python3
"""
Simple Docker check without subprocess issues
"""

import os
import sys

def check_docker_files():
    """Check if Docker files exist"""
    print("🔍 Checking Docker Files...")
    print("-" * 30)
    
    files_to_check = [
        "docker-compose.yaml",
        "Dockerfile.webapp", 
        "Dockerfile.scraper",
        "app.py",
        "database_config.py"
    ]
    
    all_exist = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_exist = False
    
    return all_exist

def check_webapp_config():
    """Check webapp configuration"""
    print("\n🌐 Checking Web App Configuration...")
    print("-" * 40)
    
    try:
        with open("app.py", "r") as f:
            content = f.read()
        
        # Check if app runs on port 5001
        if "port=5001" in content:
            print("✅ App configured for port 5001")
        else:
            print("❌ App not configured for port 5001")
        
        # Check if host is set correctly
        if "host='127.0.0.1'" in content or "host='0.0.0.0'" in content:
            print("✅ Host configuration found")
        else:
            print("❌ Host configuration missing")
        
        # Check if debug mode is on
        if "debug=True" in content:
            print("✅ Debug mode enabled")
        else:
            print("⚠️  Debug mode disabled")
            
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False
    
    return True

def check_docker_compose():
    """Check docker-compose configuration"""
    print("\n🐳 Checking Docker Compose Configuration...")
    print("-" * 45)
    
    try:
        with open("docker-compose.yaml", "r") as f:
            content = f.read()
        
        # Check for webapp service
        if "webapp:" in content:
            print("✅ Webapp service defined")
        else:
            print("❌ Webapp service missing")
        
        # Check for port mapping
        if "5001:5001" in content:
            print("✅ Port 5001 mapped correctly")
        else:
            print("❌ Port 5001 not mapped")
        
        # Check for database dependency
        if "depends_on:" in content and "database" in content:
            print("✅ Database dependency configured")
        else:
            print("❌ Database dependency missing")
            
    except Exception as e:
        print(f"❌ Error reading docker-compose.yaml: {e}")
        return False
    
    return True

def provide_manual_solutions():
    """Provide manual solutions"""
    print("\n💡 Manual Solutions:")
    print("-" * 25)
    
    print("1. 🐳 Check if Docker is running:")
    print("   - Open Docker Desktop")
    print("   - Look for green status indicator")
    
    print("\n2. 🚀 Start Docker services manually:")
    print("   - Open Command Prompt as Administrator")
    print("   - Navigate to your project folder")
    print("   - Run: docker-compose up -d")
    
    print("\n3. 🔍 Check container status:")
    print("   - Run: docker ps")
    print("   - Look for 'phygitals-webapp' container")
    
    print("\n4. 📋 Check logs:")
    print("   - Run: docker logs phygitals-webapp")
    print("   - Look for error messages")
    
    print("\n5. 🌐 Try different URLs:")
    print("   - http://localhost:5001")
    print("   - http://127.0.0.1:5001")
    print("   - http://0.0.0.0:5001")
    
    print("\n6. 🔄 Restart everything:")
    print("   - docker-compose down")
    print("   - docker-compose up -d")
    print("   - Wait 60 seconds")
    
    print("\n7. 🗄️  Check database:")
    print("   - docker logs phygitals-database")
    print("   - Look for 'ready for connections' message")

def main():
    """Main function"""
    print("🔍 Simple Docker Check")
    print("=" * 30)
    
    # Check files
    files_ok = check_docker_files()
    
    # Check webapp config
    webapp_ok = check_webapp_config()
    
    # Check docker-compose
    compose_ok = check_docker_compose()
    
    # Provide solutions
    provide_manual_solutions()
    
    print("\n" + "=" * 30)
    print("📊 Check Results:")
    print(f"  Files: {'✅ OK' if files_ok else '❌ ISSUES'}")
    print(f"  Webapp: {'✅ OK' if webapp_ok else '❌ ISSUES'}")
    print(f"  Compose: {'✅ OK' if compose_ok else '❌ ISSUES'}")
    
    if files_ok and webapp_ok and compose_ok:
        print("\n✅ Configuration looks correct!")
        print("💡 The issue is likely with Docker itself")
        print("💡 Try the manual solutions above")
    else:
        print("\n❌ Configuration issues found!")
        print("💡 Fix the issues above first")
    
    return files_ok and webapp_ok and compose_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
