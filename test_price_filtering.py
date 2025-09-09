#!/usr/bin/env python3
"""
Test the price history filtering functionality
"""

import sys
import os
import requests
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_price_filtering():
    """Test the price history filtering API"""
    print("🧪 Testing Price History Filtering")
    print("=" * 40)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test with a sample item name (you can change this)
        test_item = "Pikachu"  # Change this to an item that exists in your database
        
        print(f"🔍 Testing with item: {test_item}")
        
        # Test 1: Default filtering (exclude incomplete)
        print("\n1️⃣ Testing with default filtering (exclude incomplete):")
        response = requests.get(f"http://127.0.0.1:5001/api/price_history/{test_item}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   ✅ Got {len(data)} records (array format)")
            else:
                print(f"   ✅ Got {len(data.get('history', []))} records (object format)")
        else:
            print(f"   ❌ Error: {response.status_code}")
        
        # Test 2: Include incomplete records
        print("\n2️⃣ Testing with incomplete records included:")
        response = requests.get(f"http://127.0.0.1:5001/api/price_history/{test_item}?exclude_incomplete=false")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   ✅ Got {len(data)} records (array format)")
            else:
                print(f"   ✅ Got {len(data.get('history', []))} records (object format)")
        else:
            print(f"   ❌ Error: {response.status_code}")
        
        # Test 3: With statistics
        print("\n3️⃣ Testing with statistics:")
        response = requests.get(f"http://127.0.0.1/api/price_history/{test_item}?exclude_incomplete=true&show_stats=true")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'stats' in data:
                stats = data['stats']
                print(f"   ✅ Statistics:")
                print(f"      Total Records: {stats.get('total_records', 0):,}")
                print(f"      Complete Records: {stats.get('complete_records', 0):,}")
                print(f"      Incomplete Records: {stats.get('incomplete_records', 0):,}")
                print(f"      Filtered Records: {stats.get('filtered_records', 0):,}")
                print(f"      Excluded Records: {stats.get('excluded_records', 0):,}")
            else:
                print(f"   ⚠️  No statistics in response")
        else:
            print(f"   ❌ Error: {response.status_code}")
        
        # Test 4: Compare filtered vs unfiltered
        print("\n4️⃣ Comparing filtered vs unfiltered:")
        
        # Get filtered data
        response_filtered = requests.get(f"http://127.0.0.1:5001/api/price_history/{test_item}?exclude_incomplete=true")
        response_unfiltered = requests.get(f"http://127.0.0.1:5001/api/price_history/{test_item}?exclude_incomplete=false")
        
        if response_filtered.status_code == 200 and response_unfiltered.status_code == 200:
            filtered_data = response_filtered.json()
            unfiltered_data = response_unfiltered.json()
            
            filtered_count = len(filtered_data) if isinstance(filtered_data, list) else len(filtered_data.get('history', []))
            unfiltered_count = len(unfiltered_data) if isinstance(unfiltered_data, list) else len(unfiltered_data.get('history', []))
            
            print(f"   📊 Filtered records: {filtered_count:,}")
            print(f"   📊 Unfiltered records: {unfiltered_count:,}")
            print(f"   📊 Excluded records: {unfiltered_count - filtered_count:,}")
            
            if unfiltered_count > filtered_count:
                print(f"   ✅ Filtering is working - {unfiltered_count - filtered_count:,} incomplete records excluded")
            else:
                print(f"   ℹ️  No incomplete records found for this item")
        else:
            print(f"   ❌ Error comparing data")
        
        print("\n" + "=" * 40)
        print("🎉 Price filtering test completed!")
        print("💡 You can now use the web interface with filtering controls")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to web app")
        print("💡 Make sure the web app is running: python app_fixed.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_price_filtering()
    sys.exit(0 if success else 1)

