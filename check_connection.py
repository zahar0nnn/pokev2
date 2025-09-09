#!/usr/bin/env python3
"""
Connection diagnostic script to check what's running and fix connection issues.
"""

import socket
import requests
import subprocess
import sys
import os
from datetime import datetime

def check_port(host, port):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def check_flask_app():
    """Check if Flask app is running"""
    print("🔍 Checking Flask Application...")
    print("-" * 30)
    
    # Check if port 5001 is open
    port_open = check_port('127.0.0.1', 5001)
    print(f"Port 5001 status: {'✅ OPEN' if port_open else '❌ CLOSED'}")
    
    if port_open:
        try:
            response = requests.get('http://127.0.0.1:5001/debug', timeout=5)
            if response.status_code == 200:
                print("✅ Flask app is running and responding")
                data = response.json()
                print(f"  Data loaded: {data.get('data_loaded', 0)} items")
                return True
            else:
                print(f"❌ Flask app responded with status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Flask app not responding: {e}")
            return False
    else:
        print("❌ Flask app is not running")
        return False

def start_flask_app():
    """Start the Flask application"""
    print("\n🚀 Starting Flask Application...")
    print("-" * 35)
    
    try:
        # Check if app.py exists
        if not os.path.exists('app.py'):
            print("❌ app.py not found")
            return False
        
        print("✅ app.py found")
        print("🔄 Starting Flask app on http://127.0.0.1:5001")
        print("💡 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Start Flask app
        subprocess.run([sys.executable, 'app.py'])
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Flask app stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        return False

def check_database_connection():
    """Check database connection"""
    print("\n🗄️  Checking Database Connection...")
    print("-" * 35)
    
    try:
        from database_config import DatabaseConfig
        db = DatabaseConfig()
        connection = db.get_connection()
        
        if connection:
            print("✅ Database connection successful")
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM transactions")
            count = cursor.fetchone()[0]
            print(f"  Total transactions: {count:,}")
            cursor.close()
            connection.close()
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def provide_solutions():
    """Provide solutions for common connection issues"""
    print("\n💡 Solutions for ERR_CONNECTION_REFUSED:")
    print("-" * 45)
    
    print("1. 🔧 Start the Flask application:")
    print("   python app.py")
    print("   Then visit: http://127.0.0.1:5001")
    
    print("\n2. 🌐 Check the correct URL:")
    print("   ✅ Correct: http://127.0.0.1:5001")
    print("   ✅ Alternative: http://localhost:5001")
    print("   ❌ Wrong: http://127.0.0.1:5000 (default Flask port)")
    
    print("\n3. 🗄️  Ensure MySQL is running:")
    print("   - Start MySQL service")
    print("   - Check database connection")
    
    print("\n4. 🔍 Check firewall/antivirus:")
    print("   - Ensure port 5001 is not blocked")
    print("   - Check Windows Firewall settings")
    
    print("\n5. 🚀 Use the startup script:")
    print("   start_scraper.bat")

def main():
    """Main diagnostic function"""
    print("🔍 Connection Diagnostic Tool")
    print("=" * 40)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check Flask app
    flask_running = check_flask_app()
    
    # Check database
    db_working = check_database_connection()
    
    # Provide solutions
    provide_solutions()
    
    print("\n" + "=" * 40)
    print("📊 Diagnostic Results:")
    print(f"  Flask App: {'✅ RUNNING' if flask_running else '❌ NOT RUNNING'}")
    print(f"  Database: {'✅ WORKING' if db_working else '❌ NOT WORKING'}")
    
    if not flask_running:
        print("\n🚀 To fix ERR_CONNECTION_REFUSED:")
        print("1. Run: python app.py")
        print("2. Visit: http://127.0.0.1:5001")
        print("3. Or run: start_scraper.bat")
    
    return flask_running and db_working

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
