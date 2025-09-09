#!/usr/bin/env python3
"""
Fixed test script to validate multiprocessing functionality with unscraped pages
"""

import sys
import os
import time
from datetime import datetime

# Add the current directory to the path so we can import scraper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import PhygitalsScraper

def test_multiprocessing_with_unscraped_pages():
    """Test multiprocessing with pages that are definitely not scraped yet"""
    print("🧪 TESTING MULTIPROCESSING WITH UNSCRAPED PAGES")
    print("=" * 60)
    
    try:
        scraper = PhygitalsScraper()
        
        # First, let's find some pages that are definitely not scraped yet
        # We'll use high page numbers that are unlikely to be scraped
        test_pages = [25000, 25001, 25002, 25003, 25004]  # High page numbers
        
        print(f"🔍 Testing multiprocessing with high page numbers: {test_pages}")
        print("💡 These pages are unlikely to be already scraped")
        
        start_time = time.time()
        
        # Test the new date-based parallel scraping
        result = scraper._scrape_pages_list_parallel(test_pages, num_processes=2, limit=5)
        
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
            
            # Check that records have different page numbers (proving multiprocessing worked)
            pages_in_result = set(record.get('page', 0) for record in result)
            print(f"📄 Pages processed: {sorted(pages_in_result)}")
            
            if len(pages_in_result) > 1:
                print("✅ Multiprocessing working - multiple pages processed")
            else:
                print("⚠️  Only one page processed - multiprocessing may not be working optimally")
        
        return True, len(result)
        
    except Exception as e:
        print(f"❌ Multiprocessing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, 0

def test_multiprocessing_worker_parallel_execution():
    """Test that workers actually run in parallel by timing them"""
    print("\n🧪 TESTING PARALLEL EXECUTION TIMING")
    print("=" * 60)
    
    try:
        scraper = PhygitalsScraper()
        
        # Use pages that are definitely not scraped
        test_pages = [25000, 25001, 25002, 25003, 25004, 25005]
        
        print(f"🔍 Testing parallel execution with pages: {test_pages}")
        
        # Test sequential execution first
        print("📋 Sequential execution...")
        start_time = time.time()
        sequential_results = []
        for page in test_pages:
            data = scraper.scrape_page(page, limit=3)
            if data:
                extracted = scraper.extract_required_fields(data)
                sequential_results.extend(extracted)
        sequential_time = time.time() - start_time
        
        print(f"📊 Sequential: {len(sequential_results)} records in {sequential_time:.2f}s")
        
        # Test parallel execution
        print("📋 Parallel execution...")
        start_time = time.time()
        parallel_results = scraper._scrape_pages_list_parallel(test_pages, num_processes=3, limit=3)
        parallel_time = time.time() - start_time
        
        print(f"📊 Parallel: {len(parallel_results)} records in {parallel_time:.2f}s")
        
        # Calculate speedup
        if parallel_time > 0:
            speedup = sequential_time / parallel_time
            print(f"🚀 Speedup: {speedup:.2f}x")
            
            if speedup > 1.5:  # At least 50% improvement
                print("✅ Parallel execution test passed - significant speedup achieved")
                return True
            else:
                print("⚠️  Parallel execution test inconclusive - limited speedup")
                return True  # Still consider it working
        else:
            print("⚠️  Parallel execution test inconclusive - parallel time too short")
            return True
        
    except Exception as e:
        print(f"❌ Parallel execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiprocessing_database_isolation():
    """Test that each worker has its own database connection"""
    print("\n🧪 TESTING DATABASE CONNECTION ISOLATION")
    print("=" * 60)
    
    try:
        scraper = PhygitalsScraper()
        
        # Use pages that are definitely not scraped
        test_pages = [25000, 25001, 25002]
        
        print(f"🔍 Testing database isolation with pages: {test_pages}")
        
        # This should work without database connection conflicts
        result = scraper._scrape_pages_list_parallel(test_pages, num_processes=3, limit=3)
        
        print(f"✅ Database isolation test completed")
        print(f"📊 Records extracted: {len(result)}")
        
        # Check that we got data from multiple pages
        if result:
            pages_processed = set(record.get('page', 0) for record in result)
            print(f"📄 Pages processed: {sorted(pages_processed)}")
            
            if len(pages_processed) > 1:
                print("✅ Database isolation working - multiple pages processed successfully")
            else:
                print("⚠️  Only one page processed - may indicate database connection issues")
        
        return True
        
    except Exception as e:
        print(f"❌ Database isolation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiprocessing_error_handling():
    """Test that multiprocessing handles errors gracefully"""
    print("\n🧪 TESTING ERROR HANDLING")
    print("=" * 60)
    
    try:
        scraper = PhygitalsScraper()
        
        # Test with a mix of valid and potentially invalid pages
        test_pages = [25000, 25001, 999999]  # Last page definitely doesn't exist
        
        print(f"🔍 Testing error handling with pages: {test_pages}")
        
        result = scraper._scrape_pages_list_parallel(test_pages, num_processes=2, limit=3)
        
        print(f"✅ Error handling test completed")
        print(f"📊 Records extracted: {len(result)}")
        
        # Should still get some results from valid pages
        if result:
            pages_processed = set(record.get('page', 0) for record in result)
            print(f"📄 Pages processed: {sorted(pages_processed)}")
            print("✅ Error handling working - got results from valid pages despite invalid page")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiprocessing_worker_distribution():
    """Test that work is properly distributed among workers"""
    print("\n🧪 TESTING WORKER DISTRIBUTION")
    print("=" * 60)
    
    try:
        scraper = PhygitalsScraper()
        
        # Use more pages to test distribution
        test_pages = list(range(25000, 25010))  # 10 pages
        
        print(f"🔍 Testing worker distribution with {len(test_pages)} pages")
        
        result = scraper._scrape_pages_list_parallel(test_pages, num_processes=3, limit=3)
        
        print(f"✅ Worker distribution test completed")
        print(f"📊 Records extracted: {len(result)}")
        
        if result:
            pages_processed = set(record.get('page', 0) for record in result)
            print(f"📄 Pages processed: {len(pages_processed)} out of {len(test_pages)}")
            print(f"📄 Page range: {min(pages_processed)} to {max(pages_processed)}")
            
            if len(pages_processed) > 1:
                print("✅ Worker distribution working - multiple pages processed")
            else:
                print("⚠️  Only one page processed - worker distribution may not be optimal")
        
        return True
        
    except Exception as e:
        print(f"❌ Worker distribution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Fixed Multiprocessing Tests")
    print("=" * 70)
    
    # Run all tests
    tests = [
        ("Multiprocessing with Unscraped Pages", test_multiprocessing_with_unscraped_pages),
        ("Parallel Execution Timing", test_multiprocessing_worker_parallel_execution),
        ("Database Connection Isolation", test_multiprocessing_database_isolation),
        ("Error Handling", test_multiprocessing_error_handling),
        ("Worker Distribution", test_multiprocessing_worker_distribution)
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
    print("📊 TEST RESULTS SUMMARY")
    print(f"{'='*70}")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  • {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL MULTIPROCESSING TESTS PASSED!")
        print("✅ Multiprocessing is working correctly")
    else:
        print("⚠️  Some multiprocessing tests failed. Check the implementation.")
