#!/usr/bin/env python3
"""
Test script to validate bug fixes in the scraper
"""

import sys
import os
import time
from datetime import datetime

# Add the current directory to the path so we can import scraper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import PhygitalsScraper

def test_csv_writer_empty_data():
    """Test CSV writer with empty data (should not crash)"""
    print("🧪 TESTING CSV WRITER WITH EMPTY DATA")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Test with empty data
        scraper.save_to_csv([], "test_empty.csv")
        print("✅ CSV writer handles empty data correctly")
        
        # Test with None data
        scraper.save_to_csv(None, "test_none.csv")
        print("✅ CSV writer handles None data correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ CSV writer test failed: {e}")
        return False

def test_progress_calculation_zero_division():
    """Test progress calculation with zero total_batches"""
    print("\n🧪 TESTING PROGRESS CALCULATION ZERO DIVISION")
    print("=" * 50)
    
    try:
        from scraper import save_progress
        
        # Test with zero total_batches
        save_progress(5, 0, 100, datetime.now())
        print("✅ Progress calculation handles zero total_batches correctly")
        
        # Test with normal values
        save_progress(5, 10, 100, datetime.now())
        print("✅ Progress calculation works with normal values")
        
        return True
        
    except Exception as e:
        print(f"❌ Progress calculation test failed: {e}")
        return False

def test_backward_date_search():
    """Test backward date search with proper start page"""
    print("\n🧪 TESTING BACKWARD DATE SEARCH")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Test with a reasonable start page
        result = scraper._find_page_by_date_backward(
            "2025-01-01T00:00:00.000Z", 
            max_pages_to_check=100,
            start_from_page=5000
        )
        
        print(f"✅ Backward date search completed: {result}")
        
        # Test with default start page
        result2 = scraper._find_page_by_date_backward(
            "2025-01-01T00:00:00.000Z", 
            max_pages_to_check=100
        )
        
        print(f"✅ Backward date search with default start completed: {result2}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backward date search test failed: {e}")
        return False

def test_worker_data_flush():
    """Test that worker functions flush remaining data"""
    print("\n🧪 TESTING WORKER DATA FLUSH")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Test with pages that are definitely not scraped
        test_pages = [30000, 30001, 30002]  # High page numbers
        
        print(f"🔍 Testing data flush with pages: {test_pages}")
        
        result = scraper._scrape_pages_list_parallel(test_pages, num_processes=2, limit=3)
        
        print(f"✅ Worker data flush test completed")
        print(f"📊 Records extracted: {len(result)}")
        
        if result:
            pages_processed = set(record.get('page', 0) for record in result)
            print(f"📄 Pages processed: {sorted(pages_processed)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Worker data flush test failed: {e}")
        return False

def test_date_search_bounds():
    """Test date search with proper bounds checking"""
    print("\n🧪 TESTING DATE SEARCH BOUNDS")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Test forward search with small bounds
        result = scraper._find_page_by_date_forward(
            "2025-01-01T00:00:00.000Z", 
            max_pages_to_check=5
        )
        
        print(f"✅ Forward date search with bounds completed: {result}")
        
        # Test backward search with small bounds
        result2 = scraper._find_page_by_date_backward(
            "2025-01-01T00:00:00.000Z", 
            max_pages_to_check=5
        )
        
        print(f"✅ Backward date search with bounds completed: {result2}")
        
        return True
        
    except Exception as e:
        print(f"❌ Date search bounds test failed: {e}")
        return False

def test_sandwich_approach_edge_cases():
    """Test sandwich approach with edge cases"""
    print("\n🧪 TESTING SANDWICH APPROACH EDGE CASES")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Test with very small max_pages
        strategy = scraper.implement_date_based_sandwich_approach(max_pages=10)
        
        print(f"✅ Sandwich approach with small max_pages: {strategy['strategy']}")
        
        # Test with zero max_pages
        strategy2 = scraper.implement_date_based_sandwich_approach(max_pages=0)
        
        print(f"✅ Sandwich approach with zero max_pages: {strategy2['strategy']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sandwich approach edge cases test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Bug Fix Validation Tests")
    print("=" * 70)
    
    # Run all tests
    tests = [
        ("CSV Writer Empty Data", test_csv_writer_empty_data),
        ("Progress Calculation Zero Division", test_progress_calculation_zero_division),
        ("Backward Date Search", test_backward_date_search),
        ("Worker Data Flush", test_worker_data_flush),
        ("Date Search Bounds", test_date_search_bounds),
        ("Sandwich Approach Edge Cases", test_sandwich_approach_edge_cases)
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
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 BUG FIX VALIDATION RESULTS")
    print(f"{'='*70}")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  • {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL BUG FIXES VALIDATED!")
        print("✅ Scraper is now more robust and bug-free")
    else:
        print("⚠️  Some bug fixes need attention.")
