#!/usr/bin/env python3
"""
Test script to check database schema and date field consistency
"""

import sys
import os
from datetime import datetime

# Add the current directory to the path so we can import scraper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import PhygitalsScraper
from database_config import DatabaseConfig

def test_database_schema():
    """Test if database schema has the date field"""
    print("🧪 TESTING DATABASE SCHEMA")
    print("=" * 50)
    
    try:
        db = DatabaseConfig()
        connection = db.get_connection()
        
        if not connection:
            print("❌ Database connection failed")
            return False
        
        cursor = connection.cursor()
        
        # Check if date column exists
        cursor.execute("DESCRIBE transactions")
        columns = cursor.fetchall()
        
        print("📋 Database columns:")
        date_column_exists = False
        for column in columns:
            print(f"  • {column[0]} ({column[1]})")
            if column[0] == 'date':
                date_column_exists = True
        
        if date_column_exists:
            print("✅ Date column exists in database")
        else:
            print("❌ Date column missing from database")
            return False
        
        # Check indexes
        cursor.execute("SHOW INDEX FROM transactions")
        indexes = cursor.fetchall()
        
        print("\n📊 Database indexes:")
        date_index_exists = False
        for index in indexes:
            print(f"  • {index[2]} on {index[4]}")
            if index[4] == 'date':
                date_index_exists = True
        
        if date_index_exists:
            print("✅ Date index exists")
        else:
            print("⚠️  Date index missing (performance may be affected)")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_consistency():
    """Test if existing data has date field populated"""
    print("\n🧪 TESTING DATA CONSISTENCY")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        if not scraper.db:
            print("⚠️  Database not available - skipping data consistency test")
            return True
        
        # Get a few transactions to check
        transactions = scraper.db.get_all_transactions(limit=5)
        
        if not transactions:
            print("⚠️  No transactions in database - skipping data consistency test")
            return True
        
        print(f"✅ Retrieved {len(transactions)} transactions")
        
        # Check if date field is populated
        date_populated = 0
        for i, transaction in enumerate(transactions):
            print(f"\n📋 Transaction {i+1}:")
            print(f"  Date: {transaction.get('date', 'MISSING')}")
            print(f"  Time: {transaction.get('time', 'MISSING')}")
            print(f"  Page: {transaction.get('page', 'MISSING')}")
            
            if transaction.get('date'):
                date_populated += 1
                if transaction.get('date') == transaction.get('time'):
                    print("  ✅ Date and time match")
                else:
                    print("  ⚠️  Date and time differ")
            else:
                print("  ❌ Date field is empty")
        
        print(f"\n📊 Date field populated: {date_populated}/{len(transactions)} transactions")
        
        if date_populated == len(transactions):
            print("✅ All transactions have date field populated")
        elif date_populated > 0:
            print("⚠️  Some transactions missing date field (may need data migration)")
        else:
            print("❌ No transactions have date field populated")
        
        return date_populated > 0
        
    except Exception as e:
        print(f"❌ Data consistency test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_date_ordering():
    """Test if transactions are properly ordered by date"""
    print("\n🧪 TESTING DATE ORDERING")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        if not scraper.db:
            print("⚠️  Database not available - skipping date ordering test")
            return True
        
        # Get transactions ordered by date
        transactions = scraper.db.get_all_transactions(limit=10)
        
        if not transactions:
            print("⚠️  No transactions in database - skipping date ordering test")
            return True
        
        print(f"✅ Retrieved {len(transactions)} transactions")
        
        # Check ordering
        dates = []
        for transaction in transactions:
            date = transaction.get('date') or transaction.get('time', '')
            dates.append(date)
            print(f"  Date: {date}")
        
        # Check if dates are in descending order
        is_ordered = all(dates[i] >= dates[i+1] for i in range(len(dates)-1))
        
        if is_ordered:
            print("✅ Transactions are properly ordered by date (descending)")
        else:
            print("❌ Transactions are not properly ordered by date")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Date ordering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Database Schema and Consistency Tests")
    print("=" * 70)
    
    # Run tests
    tests = [
        ("Database Schema", test_database_schema),
        ("Data Consistency", test_data_consistency),
        ("Date Ordering", test_date_ordering)
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
    print("📊 DATABASE SCHEMA AND CONSISTENCY TEST RESULTS")
    print(f"{'='*70}")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  • {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL DATABASE TESTS PASSED!")
    else:
        print("⚠️  Some database tests failed.")
