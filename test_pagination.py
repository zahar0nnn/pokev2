#!/usr/bin/env python3
"""
Test script for pagination functionality
"""

import requests
import json
import time

def test_pagination():
    """Test pagination API endpoints"""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Pagination API...")
    print("=" * 50)
    
    # Test 1: Basic pagination
    print("\n📄 Test 1: Basic pagination")
    try:
        response = requests.get(f"{base_url}/api/data?page=1&per_page=10")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Page 1: {len(data['data'])} items")
            print(f"📊 Total count: {data['pagination']['total_count']}")
            print(f"📄 Total pages: {data['pagination']['total_pages']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Test 2: Different page sizes
    print("\n📄 Test 2: Different page sizes")
    for per_page in [5, 25, 50, 100]:
        try:
            response = requests.get(f"{base_url}/api/data?page=1&per_page={per_page}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Per page {per_page}: {len(data['data'])} items")
            else:
                print(f"❌ Error for per_page={per_page}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error for per_page={per_page}: {e}")
    
    # Test 3: Sorting
    print("\n📄 Test 3: Sorting")
    sort_options = ['date-desc', 'date-asc', 'name-asc', 'name-desc', 'price-desc', 'price-asc']
    for sort_by in sort_options:
        try:
            response = requests.get(f"{base_url}/api/data?page=1&per_page=5&sort_by={sort_by}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sort {sort_by}: {len(data['data'])} items")
                if data['data']:
                    first_item = data['data'][0]
                    print(f"   First item: {first_item.get('name', 'N/A')} - ${first_item.get('price', 0)}")
            else:
                print(f"❌ Error for sort={sort_by}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error for sort={sort_by}: {e}")
    
    # Test 4: Performance test
    print("\n📄 Test 4: Performance test")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/api/data?page=1&per_page=50")
        if response.status_code == 200:
            data = response.json()
            end_time = time.time()
            print(f"✅ Loaded {len(data['data'])} items in {end_time - start_time:.2f} seconds")
        else:
            print(f"❌ Performance test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Performance test error: {e}")
    
    # Test 5: Edge cases
    print("\n📄 Test 5: Edge cases")
    
    # Test invalid page
    try:
        response = requests.get(f"{base_url}/api/data?page=999999&per_page=10")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Invalid page: {len(data['data'])} items (should be 0)")
        else:
            print(f"❌ Invalid page error: {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid page error: {e}")
    
    # Test large per_page
    try:
        response = requests.get(f"{base_url}/api/data?page=1&per_page=2000")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Large per_page: {len(data['data'])} items (should be capped at 1000)")
        else:
            print(f"❌ Large per_page error: {response.status_code}")
    except Exception as e:
        print(f"❌ Large per_page error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Pagination tests completed!")

if __name__ == "__main__":
    test_pagination()
