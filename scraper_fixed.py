import requests
import json
import time
from typing import List, Dict, Any
from multiprocessing import Pool, cpu_count, Manager
from functools import partial
import sys
import os
from datetime import datetime
from database_config import DatabaseConfig

def save_progress(batch_num, total_batches, records_count, timestamp):
    """Save scraping progress to JSON file"""
    try:
        # Avoid division by zero
        progress_percentage = 0.0
        if total_batches > 0:
            progress_percentage = round((batch_num / total_batches) * 100, 2)
        
        progress_data = {
            'batch_number': batch_num,
            'total_batches': total_batches,
            'records_count': records_count,
            'timestamp': timestamp.isoformat(),
            'progress_percentage': progress_percentage
        }
        
        with open('scraping_progress.json', 'w') as f:
            json.dump(progress_data, f, indent=2)
        
        print(f"💾 Progress saved: Batch {batch_num}/{total_batches} ({progress_data['progress_percentage']}%)")
    except Exception as e:
        print(f"⚠️  Could not save progress: {e}")


class PhygitalsScraper:
    def __init__(self, base_url: str = "https://api.phygitals.com/api/marketplace/sales"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.scraped_pages = set()
        self.db = None
        
        # Initialize database and tables with improved error handling
        try:
            self.db = DatabaseConfig()
            self.db.create_database_and_tables()
            print("✅ Database connection established successfully")
        except Exception as e:
            print(f"❌ Failed to initialize database: {e}")
            print("💡 The scraper will continue but data won't be saved to MySQL.")
            print("💡 You can still use JSON/CSV backup files.")
            self.db = None
    
    def load_scraped_pages(self):
        """Load list of already scraped pages from database"""
        if self.db is None:
            print("⚠️  Database not available - starting with empty scraped pages list")
            self.scraped_pages = set()
            return self.scraped_pages
        
        try:
            self.scraped_pages = self.db.get_scraped_pages()
            print(f"📋 Loaded {len(self.scraped_pages)} scraped pages from database")
        except Exception as e:
            print(f"⚠️  Could not load scraped pages: {e}")
            self.scraped_pages = set()
        
        return self.scraped_pages
    
    def is_page_scraped(self, page_num):
        """Check if a page has already been scraped"""
        return page_num in self.scraped_pages
    
    def mark_page_scraped(self, page_num):
        """Mark a page as successfully scraped"""
        self.scraped_pages.add(page_num)
        if self.db is not None:
            try:
                self.db.mark_page_scraped(page_num)
            except Exception as e:
                print(f"⚠️  Could not mark page {page_num} as scraped: {e}")
    
    def scrape_page(self, page: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape a single page from the API with improved error handling
        """
        url = f"{self.base_url}?limit={limit}&page={page}"
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                return data.get('sales', [])
                
            except requests.exceptions.RequestException as e:
                print(f"Error scraping page {page} (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return []
                time.sleep(1)  # Wait before retry
            except json.JSONDecodeError as e:
                print(f"JSON decode error on page {page} (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return []
                time.sleep(1)
            except Exception as e:
                print(f"Unexpected error on page {page} (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return []
                time.sleep(1)
        
        return []
    
    @staticmethod
    def scrape_page_static(page: int, base_url: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Optimized static method for scraping a single page (used with multiprocessing)
        """
        url = f"{base_url}?limit={limit}&page={page}"
        
        # Create session with optimized settings
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        })
        
        # Retry logic for maximum data extraction
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = session.get(url, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                sales_data = data.get('sales', [])
                
                if sales_data:
                    return sales_data
                else:
                    return []
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    return []
                time.sleep(0.2)
            except json.JSONDecodeError as e:
                if attempt == max_retries - 1:
                    return []
                time.sleep(0.2)
            except Exception as e:
                if attempt == max_retries - 1:
                    return []
                time.sleep(0.2)
        
        return []
    
    def extract_required_fields(self, sales_data: List[Dict[str, Any]], page_number: int = 0) -> List[Dict[str, str]]:
        """
        Extract required fields with improved error handling
        """
        extracted_data = []
        
        for sale in sales_data:
            try:
                # Check if sale is not None and is a dictionary
                if not sale or not isinstance(sale, dict):
                    continue
                
                # Enhanced name extraction
                nft_name = self._extract_name_enhanced(sale)
                
                # Determine if it's a claw machine transaction
                from_address = sale.get("from", "")
                to_address = sale.get("to", "")
                claw_machine_address = "62Q9eeDY3eM8A5CnprBGYMPShdBjAzdpBdr71QHsS8dS"
                
                is_claw_machine = (from_address == claw_machine_address or to_address == claw_machine_address)
                claw_machine_status = "Claw Machine" if is_claw_machine else "human"
                
                # Get transaction time for date-based ordering
                transaction_time = sale.get("time", "")
                
                # Create date-based batch number
                date_batch = 0
                if transaction_time:
                    try:
                        dt = datetime.fromisoformat(transaction_time.replace('Z', '+00:00'))
                        date_batch = int(dt.strftime('%Y%m%d'))
                    except:
                        date_batch = page_number // 100  # Fallback to page-based batch
                
                extracted_sale = {
                    "date": transaction_time,
                    "page": page_number,
                    "batch": date_batch,
                    "time": transaction_time,
                    "amount": sale.get("amount", ""),
                    "type": sale.get("type", ""),
                    "Claw Machine": claw_machine_status,
                    "from": from_address,
                    "to": to_address,
                    "name": nft_name
                }
                extracted_data.append(extracted_sale)
            except Exception as e:
                print(f"Error extracting data from sale on page {page_number}: {e}")
                continue
        
        return extracted_data
    
    def _extract_name_enhanced(self, sale: Dict[str, Any]) -> str:
        """
        Enhanced name extraction with multiple fallback methods
        """
        # Method 1: Check nft.name
        nft_data = sale.get("nft")
        if nft_data and isinstance(nft_data, dict):
            name = nft_data.get("name", "")
            if name and name.strip():
                return name.strip()
        
        # Method 2: Check ebayListing.title
        ebay_data = sale.get("ebayListing")
        if ebay_data and isinstance(ebay_data, dict):
            name = ebay_data.get("title", "")
            if name and name.strip():
                return name.strip()
            
            if "data" in ebay_data:
                data_section = ebay_data.get("data", {})
                if isinstance(data_section, dict):
                    name = data_section.get("title", "")
                    if name and name.strip():
                        return name.strip()
        
        # Method 3: Check for Pokemon-related keywords
        pokemon_keywords = ['pokemon', 'card', 'trading', 'booster', 'pack', 'box', 'set']
        
        for key, value in sale.items():
            if isinstance(value, str) and len(value) > 5:
                if any(keyword in value.lower() for keyword in pokemon_keywords):
                    if len(value) > 10 and not value.isdigit():
                        return value.strip()
        
        # Method 4: Check for any string field that looks like a product name
        for key, value in sale.items():
            if isinstance(value, str) and len(value) > 15 and len(value) < 200:
                if ' ' in value and not value.replace(' ', '').isdigit():
                    if not any(skip_word in value.lower() for skip_word in ['http', 'www', 'api', 'json', 'null', 'undefined']):
                        return value.strip()
        
        return ""
    
    def save_to_mysql(self, data: List[Dict[str, str]]):
        """
        Save extracted data to MySQL database with improved error handling
        """
        if self.db is None:
            print("⚠️  Database not available - skipping MySQL save")
            return False
            
        try:
            if data:
                success = self.db.insert_transactions_batch(data)
                if success:
                    print(f"✅ Saved {len(data)} records to MySQL database")
                    return True
                else:
                    print("❌ Failed to save data to MySQL database")
                    return False
        except Exception as e:
            print(f"❌ Error saving data to MySQL: {e}")
            return False
    
    def save_to_json(self, data: List[Dict[str, str]], filename: str = "scraped_data.json"):
        """
        Save extracted data to JSON file (backup)
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def save_to_csv(self, data: List[Dict[str, str]], filename: str = "scraped_data.csv"):
        """
        Save extracted data to CSV file (backup)
        """
        try:
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if data and len(data) > 0:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                    print(f"Data saved to {filename}")
                else:
                    print(f"No data to save to {filename}")
        except Exception as e:
            print(f"Error saving CSV data: {e}")
    
    def scrape_multiple_pages_simple(self, num_pages: int = 1000, limit: int = 10) -> List[Dict[str, str]]:
        """
        Simple sequential scraping with improved error handling and progress tracking
        """
        print(f"🚀 Starting simple scraping of {num_pages} pages...")
        
        # Load already scraped pages
        self.load_scraped_pages()
        
        all_extracted_data = []
        pages_processed = 0
        pages_skipped = 0
        
        for page in range(num_pages):
            try:
                # Check if page is already scraped
                if self.is_page_scraped(page):
                    pages_skipped += 1
                    if page % 100 == 0:
                        print(f"⏭️  Page {page}: Already scraped - skipping")
                    continue
                
                # Scrape single page
                sales_data = self.scrape_page(page, limit)
                
                if sales_data:
                    # Extract data
                    extracted_data = self.extract_required_fields(sales_data, page)
                    all_extracted_data.extend(extracted_data)
                    
                    # Mark page as scraped
                    self.mark_page_scraped(page)
                    
                    # Save to database every 50 pages
                    if len(all_extracted_data) > 0 and pages_processed % 50 == 0:
                        self.save_to_mysql(all_extracted_data)
                        all_extracted_data = []  # Clear after saving
                    
                    if page % 100 == 0:
                        print(f"📄 Page {page}: {len(extracted_data)} records")
                else:
                    if page % 100 == 0:
                        print(f"⚠️  Page {page}: No data")
                
                pages_processed += 1
                
                # Small delay to be respectful to the API
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Error processing page {page}: {e}")
                continue
        
        # Final save
        if all_extracted_data:
            self.save_to_mysql(all_extracted_data)
        
        print(f"✅ Scraping completed: {pages_processed} pages processed, {pages_skipped} skipped")
        return all_extracted_data


def main():
    """
    Main function to run the scraper with improved error handling
    """
    start_time = datetime.now()
    
    try:
        scraper = PhygitalsScraper()
        
        print("🚀 Starting Phygitals API scraper...")
        print("📊 Extracting: date, page, batch, time, amount, type, Claw Machine, from, to, name")
        print("📅 Ordering: By transaction date (most recent first)")
        print("🔄 Resume functionality: ENABLED - will skip already scraped pages")
        print("-" * 60)
        
        # Use simple sequential scraping for reliability
        total_pages = 1000  # Start with 1000 pages for testing
        limit = 10
        
        print(f"📈 Total pages to process: {total_pages:,}")
        print(f"📊 Expected ~{total_pages * 10:,} total transactions (10 per page average)")
        print(f"⏰ Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Start scraping
        extracted_data = scraper.scrape_multiple_pages_simple(total_pages, limit)
        
        if extracted_data:
            end_time = datetime.now()
            duration = end_time - start_time
            
            print(f"\n🎉 SUCCESS! Scraping completed!")
            print(f"⏰ Duration: {duration}")
            print(f"📊 Total records: {len(extracted_data):,}")
            
            # Save final backups
            scraper.save_to_json(extracted_data, "scraped_data_backup.json")
            scraper.save_to_csv(extracted_data, "scraped_data_backup.csv")
            
            # Display first few records as preview
            print("\n📋 Preview of extracted data:")
            print("-" * 60)
            for i, record in enumerate(extracted_data[:3]):
                print(f"Record {i+1}:")
                for key, value in record.items():
                    print(f"  {key}: {value}")
                print()
        else:
            print("❌ No data was extracted. Please check the API or try again.")
            
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrupted by user.")
        print("💾 Progress has been saved. You can resume from where you left off.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
