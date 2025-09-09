#!/usr/bin/env python3
"""
Analyze why names are missing from the database
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_config import DatabaseConfig

def analyze_api_response():
    """Analyze a sample API response to understand the data structure"""
    print("🔍 Analyzing API Response Structure...")
    print("-" * 40)
    
    try:
        # Make a sample API call
        url = "https://api.phygitals.com/api/marketplace/sales?page=0&limit=10"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        sales_data = data.get('sales', [])
        
        print(f"📊 API Response Analysis:")
        print(f"  Total sales in response: {len(sales_data)}")
        
        if not sales_data:
            print("❌ No sales data in API response")
            return
        
        # Analyze each sale
        for i, sale in enumerate(sales_data[:5]):  # Analyze first 5 sales
            print(f"\n📋 Sale {i+1} Structure:")
            print(f"  Keys: {list(sale.keys())}")
            
            # Check for nft data
            nft_data = sale.get("nft")
            if nft_data:
                print(f"  NFT data: {nft_data}")
                if isinstance(nft_data, dict):
                    print(f"  NFT keys: {list(nft_data.keys())}")
                    print(f"  NFT name: '{nft_data.get('name', 'NOT_FOUND')}'")
                else:
                    print(f"  NFT data type: {type(nft_data)}")
            else:
                print(f"  NFT data: None")
            
            # Check for ebayListing data
            ebay_data = sale.get("ebayListing")
            if ebay_data:
                print(f"  eBay data: {ebay_data}")
                if isinstance(ebay_data, dict):
                    print(f"  eBay keys: {list(ebay_data.keys())}")
                    print(f"  eBay title: '{ebay_data.get('title', 'NOT_FOUND')}'")
                else:
                    print(f"  eBay data type: {type(ebay_data)}")
            else:
                print(f"  eBay data: None")
            
            # Check other potential name fields
            print(f"  Direct name field: '{sale.get('name', 'NOT_FOUND')}'")
            print(f"  Title field: '{sale.get('title', 'NOT_FOUND')}'")
            print(f"  Item name: '{sale.get('itemName', 'NOT_FOUND')}'")
            
            # Show the complete sale structure
            print(f"  Complete sale: {json.dumps(sale, indent=2)}")
            
            if i < 4:  # Don't show all 5, just first few
                print("  " + "-" * 50)
        
        return sales_data
        
    except Exception as e:
        print(f"❌ Error analyzing API: {e}")
        return None

def analyze_database_names():
    """Analyze name patterns in the database"""
    print("\n🗄️  Analyzing Database Name Patterns...")
    print("-" * 45)
    
    try:
        db = DatabaseConfig()
        connection = db.get_connection()
        
        if not connection:
            print("❌ Cannot connect to database")
            return False
        
        cursor = connection.cursor()
        
        # Get samples of records with empty names
        print("📋 Records with empty names:")
        cursor.execute("""
            SELECT id, time, amount, type, name, from_address, to_address, claw_machine
            FROM transactions 
            WHERE name = ''
            LIMIT 10
        """)
        empty_names = cursor.fetchall()
        
        for record in empty_names:
            print(f"  ID: {record[0]} | Time: '{record[1]}' | Amount: '{record[2]}' | Type: '{record[3]}' | Name: '{record[4]}'")
        
        # Get samples of records with non-empty names
        print(f"\n📋 Records with non-empty names:")
        cursor.execute("""
            SELECT id, time, amount, type, name, from_address, to_address, claw_machine
            FROM transactions 
            WHERE name != ''
            LIMIT 10
        """)
        non_empty_names = cursor.fetchall()
        
        for record in non_empty_names:
            print(f"  ID: {record[0]} | Time: '{record[1]}' | Amount: '{record[2]}' | Type: '{record[3]}' | Name: '{record[4]}'")
        
        # Count by name patterns
        print(f"\n📊 Name Pattern Analysis:")
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN name = '' THEN 'Empty'
                    WHEN name LIKE 'Pikachu%' THEN 'Pikachu'
                    WHEN name LIKE 'Charizard%' THEN 'Charizard'
                    WHEN name LIKE 'Blastoise%' THEN 'Blastoise'
                    WHEN name LIKE 'Squirtle%' THEN 'Squirtle'
                    WHEN name LIKE 'Charmander%' THEN 'Charmander'
                    WHEN name LIKE 'Bulbasaur%' THEN 'Bulbasaur'
                    ELSE 'Other'
                END as name_pattern,
                COUNT(*) as count
            FROM transactions 
            GROUP BY name_pattern
            ORDER BY count DESC
        """)
        patterns = cursor.fetchall()
        
        for pattern in patterns:
            print(f"  {pattern[0]}: {pattern[1]:,} records")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing database: {e}")
        return False

def test_name_extraction():
    """Test the name extraction logic"""
    print("\n🧪 Testing Name Extraction Logic...")
    print("-" * 40)
    
    # Sample API data structures that might cause issues
    test_cases = [
        {
            "name": "Normal NFT",
            "sale": {
                "time": "2025-09-08T10:00:00Z",
                "amount": "100",
                "type": "purchase",
                "nft": {
                    "name": "Pikachu #123"
                }
            }
        },
        {
            "name": "Normal eBay",
            "sale": {
                "time": "2025-09-08T10:00:00Z",
                "amount": "100",
                "type": "purchase",
                "ebayListing": {
                    "title": "Charizard Card"
                }
            }
        },
        {
            "name": "Missing NFT and eBay",
            "sale": {
                "time": "2025-09-08T10:00:00Z",
                "amount": "100",
                "type": "purchase"
            }
        },
        {
            "name": "Empty NFT name",
            "sale": {
                "time": "2025-09-08T10:00:00Z",
                "amount": "100",
                "type": "purchase",
                "nft": {
                    "name": ""
                }
            }
        },
        {
            "name": "NFT with None name",
            "sale": {
                "time": "2025-09-08T10:00:00Z",
                "amount": "100",
                "type": "purchase",
                "nft": {
                    "name": None
                }
            }
        },
        {
            "name": "NFT is None",
            "sale": {
                "time": "2025-09-08T10:00:00Z",
                "amount": "100",
                "type": "purchase",
                "nft": None
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Test: {test_case['name']}")
        sale = test_case['sale']
        
        # Apply the same logic as the scraper
        nft_data = sale.get("nft")
        ebay_data = sale.get("ebayListing")
        nft_name = ""
        
        if nft_data and isinstance(nft_data, dict):
            nft_name = nft_data.get("name", "")
        elif ebay_data and isinstance(ebay_data, dict):
            nft_name = ebay_data.get("title", "")
        
        print(f"  Result: '{nft_name}'")
        print(f"  Is empty: {nft_name == ''}")

def main():
    """Main function"""
    print("🔍 Missing Names Analysis")
    print("=" * 40)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Analyze API response
    api_data = analyze_api_response()
    
    # Analyze database patterns
    db_analysis = analyze_database_names()
    
    # Test extraction logic
    test_name_extraction()
    
    print("\n" + "=" * 40)
    print("📊 Summary:")
    print("=" * 40)
    print("Missing names can occur when:")
    print("1. 🚫 API response has no 'nft' or 'ebayListing' data")
    print("2. 🚫 NFT/eBay data exists but 'name'/'title' field is empty")
    print("3. 🚫 NFT/eBay data is None or not a dictionary")
    print("4. 🚫 API response structure changes")
    print("5. 🚫 Network errors during scraping")
    
    print("\n💡 Solutions:")
    print("1. 🔧 Improve name extraction logic")
    print("2. 🔧 Add fallback name sources")
    print("3. 🔧 Add validation before saving")
    print("4. 🔧 Retry failed extractions")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
