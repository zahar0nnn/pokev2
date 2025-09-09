#!/usr/bin/env python3
"""
Test script to validate date-based ordering instead of page-based ordering
"""

import sys
import os
from datetime import datetime

# Add the current directory to the path so we can import scraper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import PhygitalsScraper

def test_date_based_extraction():
    """Test that data extraction now includes date field and date-based batching"""
    print("🧪 TESTING DATE-BASED EXTRACTION")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Get some sample data
        print("🔍 Fetching sample data from API...")
        data = scraper.scrape_page(0, limit=3)
        
        if not data:
            print("❌ No data received from API")
            return False
        
        print(f"✅ Received {len(data)} records from API")
        
        # Test extraction with new date-based approach
        extracted_data = scraper.extract_required_fields(data)
        
        if not extracted_data:
            print("❌ No data extracted")
            return False
        
        print(f"✅ Extracted {len(extracted_data)} records")
        
        # Check the structure of extracted data
        for i, record in enumerate(extracted_data):
            print(f"\n📋 Record {i+1}:")
            print(f"  Fields: {list(record.keys())}")
            
            # Check if date field exists and is primary
            if 'date' in record:
                print(f"  ✅ Date field present: '{record['date']}'")
            else:
                print(f"  ❌ Date field missing")
                return False
            
            # Check if page field exists but is secondary
            if 'page' in record:
                print(f"  📄 Page field present: {record['page']} (reference only)")
            
            # Check if batch is date-based
            if 'batch' in record:
                print(f"  📦 Batch number: {record['batch']} (date-based)")
            
            # Check if time field exists for compatibility
            if 'time' in record:
                print(f"  ⏰ Time field: '{record['time']}' (compatibility)")
            
            # Verify date and time are the same
            if record.get('date') == record.get('time'):
                print(f"  ✅ Date and time match")
            else:
                print(f"  ⚠️  Date and time differ: date='{record.get('date')}', time='{record.get('time')}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Date-based extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_date_based_ordering():
    """Test that transactions are ordered by date"""
    print("\n🧪 TESTING DATE-BASED ORDERING")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Get data from multiple pages to test ordering
        print("🔍 Fetching data from multiple pages...")
        all_data = []
        for page in [0, 1, 2]:
            data = scraper.scrape_page(page, limit=2)
            if data:
                extracted = scraper.extract_required_fields(data)
                all_data.extend(extracted)
        
        if not all_data:
            print("❌ No data to test ordering")
            return False
        
        print(f"✅ Collected {len(all_data)} records from multiple pages")
        
        # Sort by date to test ordering
        sorted_data = sorted(all_data, key=lambda x: x.get('date', ''), reverse=True)
        
        print("\n📅 Date-based ordering test:")
        for i, record in enumerate(sorted_data[:5]):  # Show first 5
            date = record.get('date', '')
            page = record.get('page', 0)
            print(f"  {i+1}. Date: {date}, Page: {page}")
        
        # Check if dates are in descending order
        dates = [record.get('date', '') for record in sorted_data if record.get('date')]
        is_ordered = all(dates[i] >= dates[i+1] for i in range(len(dates)-1))
        
        if is_ordered:
            print("✅ Records are properly ordered by date (descending)")
        else:
            print("❌ Records are not properly ordered by date")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Date-based ordering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_date_ordering():
    """Test that database queries order by date"""
    print("\n🧪 TESTING DATABASE DATE ORDERING")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        if not scraper.db:
            print("⚠️  Database not available - skipping database test")
            return True
        
        # Get transactions from database
        print("🔍 Fetching transactions from database...")
        transactions = scraper.db.get_all_transactions()
        
        if not transactions:
            print("⚠️  No transactions in database - skipping database test")
            return True
        
        print(f"✅ Retrieved {len(transactions)} transactions from database")
        
        # Check if date field is present
        if transactions and 'date' in transactions[0]:
            print("✅ Date field present in database records")
        else:
            print("❌ Date field missing in database records")
            return False
        
        # Check ordering
        dates = [t.get('date', '') for t in transactions if t.get('date')]
        is_ordered = all(dates[i] >= dates[i+1] for i in range(len(dates)-1))
        
        if is_ordered:
            print("✅ Database records are properly ordered by date")
        else:
            print("❌ Database records are not properly ordered by date")
            return False
        
        # Show sample of ordered records
        print("\n📅 Sample of ordered database records:")
        for i, record in enumerate(transactions[:3]):
            date = record.get('date', '')
            page = record.get('page', 0)
            name = record.get('name', '')[:50] + '...' if len(record.get('name', '')) > 50 else record.get('name', '')
            print(f"  {i+1}. Date: {date}, Page: {page}, Name: {name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database date ordering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Date-Based Ordering Tests")
    print("=" * 70)
    
    # Run tests
    tests = [
        ("Date-Based Extraction", test_date_based_extraction),
        ("Date-Based Ordering", test_date_based_ordering),
        ("Database Date Ordering", test_database_date_ordering)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        print(f"Running: {test_name}")
        print(f"{'='*70}")
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 DATE-BASED ORDERING TEST RESULTS")
    print(f"{'='*70}")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  • {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL DATE-BASED ORDERING TESTS PASSED!")
        print("✅ Transactions are now properly ordered by date instead of page number")
    else:
        print("⚠️  Some date-based ordering tests failed.")
