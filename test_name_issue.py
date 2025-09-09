#!/usr/bin/env python3
"""
Simple test to identify the exact naming issue
"""

import sys
import os

# Add the current directory to the path so we can import scraper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import PhygitalsScraper

def test_name_extraction_simple():
    """Simple test to see what names are being extracted"""
    print("🧪 TESTING NAME EXTRACTION - SIMPLE VERSION")
    print("=" * 50)
    
    try:
        scraper = PhygitalsScraper()
        
        # Get one record
        data = scraper.scrape_page(0, limit=1)
        
        if not data:
            print("❌ No data received")
            return
        
        sale = data[0]
        print("Raw sale data structure:")
        print(f"Keys: {list(sale.keys())}")
        
        # Check ebayListing specifically
        if 'ebayListing' in sale:
            ebay = sale['ebayListing']
            print(f"\nebayListing type: {type(ebay)}")
            if isinstance(ebay, dict):
                print(f"ebayListing keys: {list(ebay.keys())}")
                if 'title' in ebay:
                    title = ebay['title']
                    print(f"ebayListing.title: '{title}'")
                    print(f"Title length: {len(title)}")
        
        # Test name extraction
        extracted_name = scraper._extract_name_enhanced(sale)
        print(f"\nExtracted name: '{extracted_name}'")
        print(f"Extracted name length: {len(extracted_name)}")
        
        # Test full extraction process
        full_extraction = scraper.extract_required_fields([sale])
        if full_extraction:
            record = full_extraction[0]
            print(f"\nFull record name: '{record.get('name', '')}'")
            print(f"Full record name length: {len(record.get('name', ''))}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_name_extraction_simple()
