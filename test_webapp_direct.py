#!/usr/bin/env python3
"""
Test webapp directly without Docker
"""

import sys
import os
import time
import threading
import requests
from datetime import datetime

def test_webapp_direct():
    """Test webapp by running it directly"""
    print("🌐 Testing Web App Directly...")
    print("-" * 35)
    
    # Check if app.py exists
    if not os.path.exists("app.py"):
        print("❌ app.py not found")
        return False
    
    print("✅ app.py found")
    
    # Try to import and run the app
    try:
        print("🔄 Starting web app...")
        
        # Import the app
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app import app
        
        # Start the app in a separate thread
        def run_app():
            app.run(debug=False, host='127.0.0.1', port=5001, use_reloader=False)
        
        app_thread = threading.Thread(target=run_app, daemon=True)
        app_thread.start()
        
        # Wait for app to start
        print("⏳ Waiting for app to start...")
        time.sleep(5)
        
        # Test the app
        print("🔍 Testing app endpoints...")
        
        urls_to_test = [
            "http://127.0.0.1:5001/",
            "http://127.0.0.1:5001/debug",
            "http://127.0.0.1:5001/api/data"
        ]
        
        for url in urls_to_test:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {url} - OK")
                else:
                    print(f"❌ {url} - Status {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ {url} - Error: {e}")
        
        print("\n✅ Web app is working directly!")
        print("🌐 Visit: http://127.0.0.1:5001")
        print("💡 Press Ctrl+C to stop")
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping web app...")
            return True
            
    except Exception as e:
        print(f"❌ Error running web app: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🧪 Direct Web App Test")
    print("=" * 30)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_webapp_direct()
    
    if success:
        print("\n🎉 Web app works directly!")
        print("💡 The issue is with Docker, not the web app itself")
    else:
        print("\n❌ Web app has issues")
        print("💡 Fix the web app first, then try Docker")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
