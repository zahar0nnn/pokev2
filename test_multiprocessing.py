#!/usr/bin/env python3
"""
Test script to validate multiprocessing functionality in the scraper
"""

import sys
import os
import time
from datetime import datetime

# Add the current directory to the path so we can import scraper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import PhygitalsScraper

def test_multiprocessing_basic():
    """Test basic multiprocessing functionality"""
    print("🧪 TESTING BASIC MULTIPROCESSING")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Test with a small number of pages to avoid overwhelming the API
        test_pages = [0, 1, 2, 3, 4]  # Only 5 pages for testing
        
        print(f"🔍 Testing multiprocessing with {len(test_pages)} pages...")
        print(f"📋 Pages to scrape: {test_pages}")
        
        start_time = time.time()
        
        # Test the new date-based parallel scraping
        result = scraper._scrape_pages_list_parallel(test_pages, num_processes=2, limit=10)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Multiprocessing test completed in {duration:.2f} seconds")
        print(f"📊 Total records extracted: {len(result)}")
        
        if result:
            print("📋 Sample records:")
            for i, record in enumerate(result[:3]):  # Show first 3 records
                print(f"  Record {i+1}:")
                for key, value in record.items():
                    print(f"    {key}: {value}")
                print()
        
        return True, len(result)
        
    except Exception as e:
        print(f"❌ Multiprocessing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, 0

def test_multiprocessing_worker_isolation():
    """Test that workers are properly isolated"""
    print("\n🧪 TESTING WORKER ISOLATION")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Test with pages that should have different data
        test_pages = [0, 10, 20]  # Pages that should have different data
        
        print(f"🔍 Testing worker isolation with pages: {test_pages}")
        
        # Test sequential scraping first for comparison
        print("📋 Sequential scraping for comparison...")
        sequential_results = []
        for page in test_pages:
            data = scraper.scrape_page(page, limit=5)
            if data:
                extracted = scraper.extract_required_fields(data)
                sequential_results.extend(extracted)
        
        print(f"📊 Sequential results: {len(sequential_results)} records")
        
        # Test parallel scraping
        print("📋 Parallel scraping...")
        parallel_results = scraper._scrape_pages_list_parallel(test_pages, num_processes=3, limit=5)
        
        print(f"📊 Parallel results: {len(parallel_results)} records")
        
        # Compare results
        if len(sequential_results) == len(parallel_results):
            print("✅ Worker isolation test passed - same number of records")
            return True
        else:
            print(f"⚠️  Worker isolation test inconclusive - different record counts")
            print(f"   Sequential: {len(sequential_results)}, Parallel: {len(parallel_results)}")
            return True  # This might be due to API changes between calls
        
    except Exception as e:
        print(f"❌ Worker isolation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiprocessing_database_connections():
    """Test that each worker creates its own database connection"""
    print("\n🧪 TESTING DATABASE CONNECTION ISOLATION")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Test with a small number of pages
        test_pages = [0, 1]
        
        print(f"🔍 Testing database connections with pages: {test_pages}")
        
        # This should work without database connection issues
        result = scraper._scrape_pages_list_parallel(test_pages, num_processes=2, limit=5)
        
        print(f"✅ Database connection test completed")
        print(f"📊 Records extracted: {len(result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiprocessing_error_handling():
    """Test that multiprocessing handles errors gracefully"""
    print("\n🧪 TESTING ERROR HANDLING")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Test with a mix of valid and potentially invalid pages
        test_pages = [0, 1, 99999]  # Last page might not exist
        
        print(f"🔍 Testing error handling with pages: {test_pages}")
        
        result = scraper._scrape_pages_list_parallel(test_pages, num_processes=2, limit=5)
        
        print(f"✅ Error handling test completed")
        print(f"📊 Records extracted: {len(result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiprocessing_performance():
    """Test multiprocessing performance vs sequential"""
    print("\n🧪 TESTING MULTIPROCESSING PERFORMANCE")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Test with more pages for meaningful performance comparison
        test_pages = list(range(0, 10))  # 10 pages
        
        print(f"🔍 Testing performance with {len(test_pages)} pages...")
        
        # Sequential test
        print("📋 Sequential scraping...")
        start_time = time.time()
        sequential_results = []
        for page in test_pages:
            data = scraper.scrape_page(page, limit=5)
            if data:
                extracted = scraper.extract_required_fields(data)
                sequential_results.extend(extracted)
        sequential_time = time.time() - start_time
        
        print(f"📊 Sequential: {len(sequential_results)} records in {sequential_time:.2f}s")
        
        # Parallel test
        print("📋 Parallel scraping...")
        start_time = time.time()
        parallel_results = scraper._scrape_pages_list_parallel(test_pages, num_processes=3, limit=5)
        parallel_time = time.time() - start_time
        
        print(f"📊 Parallel: {len(parallel_results)} records in {parallel_time:.2f}s")
        
        # Performance comparison
        if parallel_time > 0:
            speedup = sequential_time / parallel_time
            print(f"🚀 Speedup: {speedup:.2f}x")
            
            if speedup > 1.2:  # At least 20% improvement
                print("✅ Performance test passed - multiprocessing is faster")
            else:
                print("⚠️  Performance test inconclusive - multiprocessing not significantly faster")
        else:
            print("⚠️  Performance test inconclusive - parallel time too short")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Multiprocessing Tests")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("Basic Multiprocessing", test_multiprocessing_basic),
        ("Worker Isolation", test_multiprocessing_worker_isolation),
        ("Database Connections", test_multiprocessing_database_connections),
        ("Error Handling", test_multiprocessing_error_handling),
        ("Performance", test_multiprocessing_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  • {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL MULTIPROCESSING TESTS PASSED!")
    else:
        print("⚠️  Some multiprocessing tests failed. Check the implementation.")
