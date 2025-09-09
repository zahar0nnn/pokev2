#!/usr/bin/env python3
"""
Test script to check if names are being truncated during storage or display
"""

import sys
import os
import json

# Add the current directory to the path so we can import scraper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import PhygitalsScraper

def test_name_storage_and_retrieval():
    """Test if names are being truncated during storage or retrieval"""
    print("🧪 TESTING NAME STORAGE AND RETRIEVAL")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Get some actual data
        print("🔍 Fetching sample data from API...")
        data = scraper.scrape_page(0, limit=3)
        
        if not data:
            print("❌ No data received from API")
            return False
        
        print(f"✅ Received {len(data)} records from API")
        
        # Test the full extraction process
        for i, sale in enumerate(data):
            print(f"\n📋 Record {i+1}:")
            
            # Extract using the full process
            extracted_data = scraper.extract_required_fields([sale])
            
            if extracted_data:
                record = extracted_data[0]
                name = record.get('name', '')
                print(f"Extracted name: '{name}'")
                print(f"Name length: {len(name)}")
                
                # Check if the name looks truncated
                if name.endswith('&') or name.endswith('...') or (len(name) > 50 and not name.endswith('10')):
                    print("⚠️  POTENTIAL TRUNCATION DETECTED!")
                
                # Show the full record
                print("Full extracted record:")
                for key, value in record.items():
                    if key == 'name':
                        print(f"  {key}: '{value}' (length: {len(value)})")
                    else:
                        print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Name storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_name_storage():
    """Test if names are being truncated in the database"""
    print("\n🧪 TESTING DATABASE NAME STORAGE")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Check the database schema for name field length
        if scraper.db:
            connection = scraper.db.get_connection()
            if connection:
                cursor = connection.cursor()
                
                # Check the table structure
                cursor.execute("DESCRIBE transactions")
                columns = cursor.fetchall()
                
                print("Database table structure:")
                for column in columns:
                    print(f"  {column[0]}: {column[1]} {column[2] if len(column) > 2 else ''}")
                
                # Check for any existing records with long names
                cursor.execute("SELECT name, LENGTH(name) as name_length FROM transactions WHERE LENGTH(name) > 50 ORDER BY name_length DESC LIMIT 5")
                long_names = cursor.fetchall()
                
                print(f"\nLongest names in database:")
                for name, length in long_names:
                    print(f"  Length {length}: '{name}'")
                
                cursor.close()
                connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database name storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_truncation_cases():
    """Test specific cases that might cause truncation"""
    print("\n🧪 TESTING SPECIFIC TRUNCATION CASES")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Test with various name lengths
        test_names = [
            "2023 Pokemon Japanese Scarlet & Violet Booster Box",
            "2023 Pokemon Japanese Scarlet &",
            "2024 ONE PIECE SIMPLIFIED CHINESE 1ST ANV SET #025 RORONOA ZORO PSA 10",
            "Short Name",
            "A" * 200,  # Very long name
            "2023 Pokemon Japanese Scarlet & Violet Booster Box Set Complete"
        ]
        
        for i, test_name in enumerate(test_names):
            print(f"\nTest {i+1}: '{test_name}'")
            print(f"Length: {len(test_name)}")
            
            # Create mock sale data
            mock_sale = {
                "time": "2025-01-01T00:00:00.000Z",
                "amount": "1000000",
                "type": "sale",
                "from": "test_from",
                "to": "test_to",
                "ebayListing": {
                    "title": test_name
                }
            }
            
            # Extract name
            extracted_name = scraper._extract_name_enhanced(mock_sale)
            print(f"Extracted: '{extracted_name}'")
            print(f"Match: {extracted_name == test_name}")
            
            if extracted_name != test_name:
                print("❌ NAME MISMATCH DETECTED!")
                print(f"Original: '{test_name}'")
                print(f"Extracted: '{extracted_name}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Specific truncation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Name Storage Debug Tests")
    print("=" * 70)
    
    # Run tests
    test1_passed = test_name_storage_and_retrieval()
    test2_passed = test_database_name_storage()
    test3_passed = test_specific_truncation_cases()
    
    print(f"\n📊 TEST RESULTS:")
    print(f"  • Name storage and retrieval: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  • Database name storage: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"  • Specific truncation cases: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed and test3_passed:
        print(f"\n🎉 All name storage tests completed!")
    else:
        print(f"\n⚠️  Some name storage tests failed.")
