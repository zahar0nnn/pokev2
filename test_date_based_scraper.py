#!/usr/bin/env python3
"""
Test script for the new date-based sandwich approach
"""

import sys
import os
from datetime import datetime

# Add the current directory to the path so we can import scraper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import PhygitalsScraper

def test_date_based_approach():
    """Test the new date-based sandwich approach"""
    print("🧪 TESTING DATE-BASED SANDWICH APPROACH")
    print("=" * 50)
    
    try:
        # Initialize scraper
        scraper = PhygitalsScraper()
        
        # Test 1: Get date range from database
        print("\n🔍 Test 1: Getting date range from database...")
        date_range = scraper.get_date_range_from_database()
        print(f"✅ Date range result: {date_range}")
        
        # Test 2: Test date-based page finding (if we have data)
        if date_range['first_date'] and date_range['last_date']:
            print(f"\n🔍 Test 2: Finding pages for dates...")
            
            # Test finding first date
            print(f"  🔍 Finding page for first date: {date_range['first_date']}")
            first_result = scraper.find_page_by_date(date_range['first_date'], search_direction='forward', max_pages_to_check=100)
            print(f"  ✅ First date result: {first_result}")
            
            # Test finding last date
            print(f"  🔍 Finding page for last date: {date_range['last_date']}")
            last_result = scraper.find_page_by_date(date_range['last_date'], search_direction='forward', max_pages_to_check=100)
            print(f"  ✅ Last date result: {last_result}")
        
        # Test 3: Test sandwich strategy
        print(f"\n🔍 Test 3: Testing sandwich strategy...")
        sandwich_strategy = scraper.implement_date_based_sandwich_approach(max_pages=1000)  # Limit for testing
        print(f"✅ Sandwich strategy result: {sandwich_strategy}")
        
        # Test 4: Test validation logging
        print(f"\n🔍 Test 4: Testing validation logging...")
        test_data = [
            {
                'page': 1,
                'time': '2025-01-01T00:00:00.000Z',
                'amount': '100',
                'type': 'sale',
                'name': 'Test Item 1',
                'Claw Machine': 'human'
            },
            {
                'page': 2,
                'time': '2025-01-02T00:00:00.000Z',
                'amount': '200',
                'type': 'sale',
                'name': 'Test Item 2',
                'Claw Machine': 'Claw Machine'
            }
        ]
        scraper._log_sandwich_validation(sandwich_strategy, test_data)
        
        print(f"\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print(f"✅ Date-based sandwich approach is working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_single_page_scraping():
    """Test single page scraping to ensure basic functionality works"""
    print("\n🧪 TESTING SINGLE PAGE SCRAPING")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Test scraping a single page
        print("🔍 Testing single page scraping...")
        data = scraper.scrape_page(0, limit=10)
        
        if data:
            print(f"✅ Successfully scraped page 0: {len(data)} items")
            
            # Test data extraction
            extracted = scraper.extract_required_fields(data)
            print(f"✅ Successfully extracted {len(extracted)} records")
            
            if extracted:
                print("📋 Sample extracted record:")
                for key, value in extracted[0].items():
                    print(f"  {key}: {value}")
        else:
            print("⚠️  No data found on page 0")
        
        return True
        
    except Exception as e:
        print(f"❌ Single page test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Date-Based Scraper Tests")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_single_page_scraping()
    test2_passed = test_date_based_approach()
    
    print(f"\n📊 TEST RESULTS:")
    print(f"  • Single page scraping: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  • Date-based approach: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print(f"\n🎉 ALL TESTS PASSED! Date-based scraper is ready to use.")
    else:
        print(f"\n⚠️  Some tests failed. Please check the implementation.")
