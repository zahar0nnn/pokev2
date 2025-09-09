#!/usr/bin/env python3
"""
Test script to debug name extraction issues
"""

import sys
import os
import json

# Add the current directory to the path so we can import scraper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import PhygitalsScraper

def test_name_extraction():
    """Test name extraction with actual API data"""
    print("🧪 TESTING NAME EXTRACTION")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Get some actual data from the API
        print("🔍 Fetching sample data from API...")
        data = scraper.scrape_page(0, limit=5)
        
        if not data:
            print("❌ No data received from API")
            return False
        
        print(f"✅ Received {len(data)} records from API")
        
        # Test name extraction on each record
        for i, sale in enumerate(data):
            print(f"\n📋 Record {i+1}:")
            print(f"Raw sale data keys: {list(sale.keys())}")
            
            # Show the raw data structure
            print("Raw sale data:")
            print(json.dumps(sale, indent=2, default=str))
            
            # Test name extraction
            extracted_name = scraper._extract_name_enhanced(sale)
            print(f"Extracted name: '{extracted_name}'")
            
            # Test each extraction method individually
            print("\n🔍 Testing individual extraction methods:")
            
            # Method 1: nft.name
            nft_data = sale.get("nft")
            if nft_data and isinstance(nft_data, dict):
                nft_name = nft_data.get("name", "")
                print(f"  Method 1 (nft.name): '{nft_name}'")
            else:
                print(f"  Method 1 (nft.name): No nft data")
            
            # Method 2: ebayListing.title
            ebay_data = sale.get("ebayListing")
            if ebay_data and isinstance(ebay_data, dict):
                ebay_title = ebay_data.get("title", "")
                print(f"  Method 2 (ebayListing.title): '{ebay_title}'")
                
                if "data" in ebay_data:
                    data_section = ebay_data.get("data", {})
                    if isinstance(data_section, dict):
                        data_title = data_section.get("title", "")
                        print(f"  Method 2b (ebayListing.data.title): '{data_title}'")
            else:
                print(f"  Method 2 (ebayListing.title): No ebayListing data")
            
            # Method 3: Pokemon keywords
            pokemon_keywords = ['pokemon', 'card', 'trading', 'booster', 'pack', 'box', 'set']
            found_keywords = []
            for key, value in sale.items():
                if isinstance(value, str) and len(value) > 5:
                    if any(keyword in value.lower() for keyword in pokemon_keywords):
                        found_keywords.append(f"{key}: '{value}'")
            print(f"  Method 3 (Pokemon keywords): {found_keywords}")
            
            # Method 4: String fields that look like product names
            product_like_fields = []
            for key, value in sale.items():
                if isinstance(value, str) and len(value) > 15 and len(value) < 200:
                    if ' ' in value and not value.replace(' ', '').isdigit():
                        if not any(skip_word in value.lower() for skip_word in ['http', 'www', 'api', 'json', 'null', 'undefined']):
                            product_like_fields.append(f"{key}: '{value}'")
            print(f"  Method 4 (Product-like fields): {product_like_fields}")
            
            print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Name extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_naming_issue():
    """Test the specific naming issue mentioned"""
    print("\n🧪 TESTING SPECIFIC NAMING ISSUE")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Create a mock sale object that might have the naming issue
        mock_sale = {
            "time": "2025-01-01T00:00:00.000Z",
            "amount": "1000000",
            "type": "sale",
            "from": "test_from",
            "to": "test_to",
            "nft": {
                "name": "2023 Pokemon Japanese Scarlet & Violet"
            },
            "ebayListing": {
                "title": "2023 Pokemon Japanese Scarlet & Violet Booster Box"
            }
        }
        
        print("🔍 Testing with mock sale data:")
        print(f"Mock sale: {json.dumps(mock_sale, indent=2)}")
        
        extracted_name = scraper._extract_name_enhanced(mock_sale)
        print(f"Extracted name: '{extracted_name}'")
        
        # Test what happens with truncated names
        truncated_name = "2023 Pokemon Japanese Scarlet &"
        print(f"Truncated name: '{truncated_name}'")
        print(f"Length: {len(truncated_name)}")
        print(f"Contains Pokemon keyword: {'pokemon' in truncated_name.lower()}")
        print(f"Length > 10: {len(truncated_name) > 10}")
        print(f"Is digit: {truncated_name.isdigit()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Specific naming issue test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Name Extraction Debug Tests")
    print("=" * 70)
    
    # Run tests
    test1_passed = test_name_extraction()
    test2_passed = test_specific_naming_issue()
    
    print(f"\n📊 TEST RESULTS:")
    print(f"  • Name extraction test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  • Specific naming issue test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print(f"\n🎉 All name extraction tests completed!")
    else:
        print(f"\n⚠️  Some name extraction tests failed.")
