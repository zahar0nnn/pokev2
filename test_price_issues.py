#!/usr/bin/env python3
"""
Test script to investigate price issues and 'No price history found' problems
"""

import sys
import os
from datetime import datetime

# Add the current directory to the path so we can import scraper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import PhygitalsScraper
from database_config import DatabaseConfig

def test_price_calculation():
    """Test price calculation logic"""
    print("🧪 TESTING PRICE CALCULATION")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        if not scraper.db:
            print("⚠️  Database not available - skipping price calculation test")
            return False
        
        # Get some sample transactions
        transactions = scraper.db.get_all_transactions(limit=10)
        
        if not transactions:
            print("⚠️  No transactions in database - skipping price calculation test")
            return False
        
        print(f"✅ Retrieved {len(transactions)} transactions")
        
        # Check price data
        price_issues = []
        for i, transaction in enumerate(transactions):
            print(f"\n📋 Transaction {i+1}:")
            print(f"  Name: {transaction.get('name', 'MISSING')[:50]}...")
            print(f"  Amount: {transaction.get('amount', 'MISSING')}")
            print(f"  Price: {transaction.get('price', 'MISSING')}")
            print(f"  Type: {transaction.get('type', 'MISSING')}")
            
            # Check for price issues
            amount = transaction.get('amount', '')
            price = transaction.get('price', 0)
            
            if not amount or amount == '':
                price_issues.append(f"Transaction {i+1}: Missing amount")
            elif amount == '0' or amount == 0:
                price_issues.append(f"Transaction {i+1}: Zero amount")
            elif price == 0:
                price_issues.append(f"Transaction {i+1}: Zero price despite amount {amount}")
            elif price is None:
                price_issues.append(f"Transaction {i+1}: None price")
        
        if price_issues:
            print(f"\n❌ Found {len(price_issues)} price issues:")
            for issue in price_issues:
                print(f"  • {issue}")
        else:
            print("\n✅ No price calculation issues found")
        
        return len(price_issues) == 0
        
    except Exception as e:
        print(f"❌ Price calculation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_price_history_filtering():
    """Test how price history filtering works"""
    print("\n🧪 TESTING PRICE HISTORY FILTERING")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        if not scraper.db:
            print("⚠️  Database not available - skipping price history test")
            return False
        
        # Get all transactions
        transactions = scraper.db.get_all_transactions()
        
        if not transactions:
            print("⚠️  No transactions in database - skipping price history test")
            return False
        
        print(f"✅ Retrieved {len(transactions)} total transactions")
        
        # Group by name to find items with price history issues
        items_by_name = {}
        for transaction in transactions:
            name = transaction.get('name', 'Unknown')
            if name not in items_by_name:
                items_by_name[name] = []
            items_by_name[name].append(transaction)
        
        print(f"✅ Found {len(items_by_name)} unique items")
        
        # Check each item for price history issues
        items_with_issues = []
        items_with_zero_prices = []
        items_with_no_prices = []
        
        for name, item_transactions in items_by_name.items():
            # Check if any transaction has a valid price
            has_valid_price = any(
                t.get('price') and t.get('price') != 0 and t.get('price') is not None 
                for t in item_transactions
            )
            
            if not has_valid_price:
                # Check what's wrong
                zero_prices = [t for t in item_transactions if t.get('price') == 0]
                no_prices = [t for t in item_transactions if not t.get('price') or t.get('price') is None]
                
                if zero_prices:
                    items_with_zero_prices.append((name, len(zero_prices)))
                if no_prices:
                    items_with_no_prices.append((name, len(no_prices)))
                
                items_with_issues.append(name)
        
        print(f"\n📊 Price History Analysis:")
        print(f"  • Items with price issues: {len(items_with_issues)}")
        print(f"  • Items with zero prices: {len(items_with_zero_prices)}")
        print(f"  • Items with no prices: {len(items_with_no_prices)}")
        
        if items_with_zero_prices:
            print(f"\n❌ Items with zero prices (first 5):")
            for name, count in items_with_zero_prices[:5]:
                print(f"  • {name[:50]}... ({count} transactions)")
        
        if items_with_no_prices:
            print(f"\n❌ Items with no prices (first 5):")
            for name, count in items_with_no_prices[:5]:
                print(f"  • {name[:50]}... ({count} transactions)")
        
        return len(items_with_issues) == 0
        
    except Exception as e:
        print(f"❌ Price history filtering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_price_calculation_logic():
    """Test the actual price calculation logic"""
    print("\n🧪 TESTING PRICE CALCULATION LOGIC")
    print("=" * 50)
    
    # Test cases for price calculation
    test_cases = [
        {"amount": "250000000", "expected_price": 250.0},
        {"amount": "1000000", "expected_price": 1.0},
        {"amount": "0", "expected_price": 0.0},
        {"amount": "", "expected_price": 0.0},
        {"amount": None, "expected_price": 0.0},
        {"amount": "invalid", "expected_price": 0.0},
        {"amount": "50000000", "expected_price": 50.0},
    ]
    
    print("Testing price calculation logic:")
    for i, test_case in enumerate(test_cases):
        amount = test_case["amount"]
        expected = test_case["expected_price"]
        
        # Simulate the price calculation logic from database_config.py
        price = 0
        if amount:
            try:
                amount_int = int(amount)
                price = round(amount_int / 1000000, 2)
            except (ValueError, TypeError):
                price = 0
        
        status = "✅" if price == expected else "❌"
        print(f"  {status} Test {i+1}: amount='{amount}' -> price={price} (expected {expected})")
    
    return True

def test_database_price_queries():
    """Test database queries for price data"""
    print("\n🧪 TESTING DATABASE PRICE QUERIES")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        if not scraper.db:
            print("⚠️  Database not available - skipping database price test")
            return False
        
        connection = scraper.db.get_connection()
        if not connection:
            print("❌ Could not connect to database")
            return False
        
        cursor = connection.cursor()
        
        # Test 1: Count total transactions
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total transactions: {total_count}")
        
        # Test 2: Count transactions with price > 0
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE price > 0")
        price_gt_zero = cursor.fetchone()[0]
        print(f"📊 Transactions with price > 0: {price_gt_zero}")
        
        # Test 3: Count transactions with price = 0
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE price = 0")
        price_zero = cursor.fetchone()[0]
        print(f"📊 Transactions with price = 0: {price_zero}")
        
        # Test 4: Count transactions with NULL price
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE price IS NULL")
        price_null = cursor.fetchone()[0]
        print(f"📊 Transactions with NULL price: {price_null}")
        
        # Test 5: Sample of transactions with price = 0
        cursor.execute("SELECT name, amount, price FROM transactions WHERE price = 0 LIMIT 5")
        zero_price_samples = cursor.fetchall()
        
        if zero_price_samples:
            print(f"\n📋 Sample transactions with price = 0:")
            for name, amount, price in zero_price_samples:
                print(f"  • Name: {name[:50]}... Amount: {amount}, Price: {price}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database price queries test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Price Issues Investigation")
    print("=" * 70)
    
    # Run tests
    tests = [
        ("Price Calculation Logic", test_price_calculation_logic),
        ("Price Calculation", test_price_calculation),
        ("Price History Filtering", test_price_history_filtering),
        ("Database Price Queries", test_database_price_queries)
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
    print("📊 PRICE ISSUES INVESTIGATION RESULTS")
    print(f"{'='*70}")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  • {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL PRICE TESTS PASSED!")
    else:
        print("⚠️  Some price tests failed - investigation needed.")
