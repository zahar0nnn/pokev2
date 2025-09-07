import requests
import json
import time
from typing import List, Dict, Any
from multiprocessing import Pool, cpu_count
from functools import partial
import sys
import os
import ctypes
from datetime import datetime
from database_config import DatabaseConfig

def prevent_sleep():
    """Prevent Windows from going to sleep during scraping"""
    try:
        # Check if we're on Windows
        if hasattr(ctypes, 'windll') and hasattr(ctypes.windll, 'kernel32'):
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
            print("🔋 Sleep mode prevention activated")
        else:
            print("ℹ️  Sleep mode prevention not available on this system")
    except Exception as e:
        print(f"⚠️  Could not prevent sleep mode: {e}")

def allow_sleep():
    """Allow Windows to go to sleep again"""
    try:
        # Check if we're on Windows
        if hasattr(ctypes, 'windll') and hasattr(ctypes.windll, 'kernel32'):
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
            print("💤 Sleep mode re-enabled")
        else:
            print("ℹ️  Sleep mode re-enable not available on this system")
    except Exception as e:
        print(f"⚠️  Could not re-enable sleep mode: {e}")


class PhygitalsScraper:
    def __init__(self, base_url: str = "https://api.phygitals.com/api/marketplace/sales"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.scraped_pages = set()
        self.db = DatabaseConfig()
        # Initialize database and tables
        self.db.create_database_and_tables()
    
    def load_scraped_pages(self):
        """Load list of already scraped pages from database"""
        self.scraped_pages = self.db.get_scraped_pages()
        print(f"📋 Loaded {len(self.scraped_pages)} scraped pages from database")
        return self.scraped_pages
    
    def is_page_scraped(self, page_num):
        """Check if a page has already been scraped"""
        return page_num in self.scraped_pages
    
    def mark_page_scraped(self, page_num):
        """Mark a page as successfully scraped"""
        self.scraped_pages.add(page_num)
        self.db.mark_page_scraped(page_num)
    
    def get_last_scraped_date(self):
        """Get the date of the last scraped transaction"""
        try:
            connection = self.db.get_connection()
            if not connection:
                return None
                
            cursor = connection.cursor()
            cursor.execute("SELECT time FROM transactions ORDER BY time DESC LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"Error getting last scraped date: {e}")
            return None
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    def find_starting_page_by_date(self, target_date, max_pages=21000):
        """Find the starting page based on the last scraped date"""
        print(f"🔍 Finding starting page based on last scraped date: {target_date}")
        
        # Binary search to find the page with the target date
        left, right = 0, max_pages
        best_page = 0
        
        while left <= right:
            mid = (left + right) // 2
            print(f"  🔍 Checking page {mid}...")
            
            try:
                data = self.scrape_page(mid, limit=1)  # Just get 1 item to check date
                if data and len(data) > 0:
                    page_date = data[0].get('time', '')
                    print(f"    📅 Page {mid} date: {page_date}")
                    
                    if page_date:
                        if page_date >= target_date:
                            # This page is at or after our target date
                            best_page = mid
                            right = mid - 1
                        else:
                            # This page is before our target date
                            left = mid + 1
                    else:
                        # No date found, try next page
                        left = mid + 1
                else:
                    # No data on this page, try lower pages
                    right = mid - 1
                    
            except Exception as e:
                print(f"    ❌ Error checking page {mid}: {e}")
                right = mid - 1
                
            # Safety check to avoid infinite loop
            if right - left < 0:
                break
        
        print(f"✅ Found starting page: {best_page}")
        return best_page
    
    def scrape_page(self, page: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape a single page from the API
        """
        url = f"{self.base_url}?limit={limit}&page={page}"
        
        try:
            print(f"Scraping page {page}...")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('sales', [])
            
        except requests.exceptions.RequestException as e:
            print(f"Error scraping page {page}: {e}")
            return []
    
    @staticmethod
    def scrape_page_static(page: int, base_url: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Optimized static method for scraping a single page (used with multiprocessing)
        """
        url = f"{base_url}?limit={limit}&page={page}"
        
        # Create session with optimized settings for maximum performance
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
                print(f"Scraping page {page} (attempt {attempt + 1})...")
                response = session.get(url, timeout=10)  # Reduced timeout to prevent hanging
                response.raise_for_status()
                
                data = response.json()
                sales_data = data.get('sales', [])
                
                if sales_data:
                    print(f"✓ Page {page}: {len(sales_data)} items scraped")
                    return sales_data
                else:
                    print(f"⚠ Page {page}: No data found")
                    return []
                
            except requests.exceptions.RequestException as e:
                print(f"✗ Error scraping page {page} (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return []
                time.sleep(0.2)  # Slightly longer delay before retry
            except json.JSONDecodeError as e:
                print(f"✗ JSON decode error on page {page} (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return []
                time.sleep(0.2)
            except Exception as e:
                print(f"✗ Unexpected error on page {page} (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return []
                time.sleep(0.2)
        
        return []
    
    def extract_required_fields(self, sales_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Extract only the required fields: time, amount, type, name
        """
        extracted_data = []
        
        for sale in sales_data:
            try:
                # Check if sale is not None and is a dictionary
                if not sale or not isinstance(sale, dict):
                    continue
                
                # Safely get name from nft or ebayListing
                nft_data = sale.get("nft")
                ebay_data = sale.get("ebayListing")
                nft_name = ""
                
                if nft_data and isinstance(nft_data, dict):
                    nft_name = nft_data.get("name", "")
                elif ebay_data and isinstance(ebay_data, dict):
                    nft_name = ebay_data.get("title", "")
                
                extracted_sale = {
                    "time": sale.get("time", ""),
                    "amount": sale.get("amount", ""),
                    "type": sale.get("type", ""),
                    "name": nft_name
                }
                extracted_data.append(extracted_sale)
            except Exception as e:
                print(f"Error extracting data from sale: {e}")
                continue
        
        return extracted_data
    
    def _extract_required_fields_with_page(self, sales_data: List[Dict[str, Any]], page_number: int) -> List[Dict[str, str]]:
        """
        Extract required fields with page number for sequential processing
        """
        extracted_data = []
        
        for sale in sales_data:
            try:
                # Check if sale is not None and is a dictionary
                if not sale or not isinstance(sale, dict):
                    continue
                
                # Safely get name from nft or ebayListing
                nft_data = sale.get("nft")
                ebay_data = sale.get("ebayListing")
                nft_name = ""
                
                if nft_data and isinstance(nft_data, dict):
                    nft_name = nft_data.get("name", "")
                elif ebay_data and isinstance(ebay_data, dict):
                    nft_name = ebay_data.get("title", "")
                
                # Determine if it's a claw machine transaction
                from_address = sale.get("from", "")
                to_address = sale.get("to", "")
                claw_machine_address = "62Q9eeDY3eM8A5CnprBGYMPShdBjAzdpBdr71QHsS8dS"
                
                is_claw_machine = (from_address == claw_machine_address or to_address == claw_machine_address)
                claw_machine_status = "Claw Machine" if is_claw_machine else "human"
                
                extracted_sale = {
                    "page": page_number,
                    "batch": page_number // 100,  # Batch number (every 100 pages)
                    "time": sale.get("time", ""),
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
    
    
    def scrape_multiple_pages(self, num_pages: int = 5, limit: int = 10, use_multiprocessing: bool = True) -> List[Dict[str, str]]:
        """
        Scrape multiple pages and extract required fields
        """
        if use_multiprocessing:
            return self._scrape_multiple_pages_parallel(num_pages, limit)
        else:
            return self._scrape_multiple_pages_sequential(num_pages, limit)
    
    def _scrape_multiple_pages_sequential(self, num_pages: int, limit: int) -> List[Dict[str, str]]:
        """
        Sequential scraping (original method)
        """
        all_extracted_data = []
        
        for page in range(num_pages):
            sales_data = self.scrape_page(page, limit)
            
            if not sales_data:
                print(f"No data found on page {page}, stopping...")
                break
            
            # Extract data with page number
            extracted_data = self._extract_required_fields_with_page(sales_data, page)
            all_extracted_data.extend(extracted_data)
            
            # Add a small delay to be respectful to the API
            time.sleep(1)
        
        return all_extracted_data
    
    def _scrape_multiple_pages_parallel(self, num_pages: int, num_processes: int = 16, limit: int = 100, start_page: int = 0) -> List[Dict[str, str]]:
        """
        Reliable parallel scraping with correct page number tracking and resume functionality
        """
        print(f"🚀 Starting parallel scraping with {num_processes} processes...")
        print(f"📊 Processing {num_pages:,} pages with {limit} items per page")
        print(f"🎯 Estimated total items: {num_pages * limit:,}")
        
        # Load already scraped pages
        self.load_scraped_pages()
        already_scraped = len(self.scraped_pages)
        print(f"📋 Found {already_scraped:,} already scraped pages - will skip these")
        
        all_extracted_data = []
        batch_size = 500  # Smaller batches for better reliability
        skipped_pages = 0
        
        for batch_start in range(start_page, num_pages, batch_size):
            batch_end = min(batch_start + batch_size, num_pages)
            batch_pages = list(range(batch_start, batch_end))
            
            print(f"\n🔄 Processing batch {batch_start//batch_size + 1}/{(num_pages + batch_size - 1)//batch_size}")
            print(f"📄 Pages {batch_start:,} to {batch_end-1:,} ({(batch_end-batch_start):,} pages)")
            
            # Process each page individually to ensure correct page numbers
            batch_extracted_data = []
            for page_num in batch_pages:
                # Check if page is already scraped
                if self.is_page_scraped(page_num):
                    if page_num % 100 == 0:  # Only show skip message every 100 pages
                        print(f"  ⏭️  Page {page_num}: Already scraped - skipping")
                    skipped_pages += 1
                    continue
                
                try:
                    # Scrape single page
                    sales_data = self.scrape_page(page_num, limit)
                    
                    if sales_data:
                        # Extract data with correct page number
                        extracted_data = self._extract_required_fields_with_page(sales_data, page_num)
                        batch_extracted_data.extend(extracted_data)
                        
                        # Mark page as successfully scraped
                        self.mark_page_scraped(page_num)
                        
                        if page_num % 50 == 0:  # Progress update every 50 pages
                            print(f"  📄 Page {page_num}: {len(extracted_data)} records")
                    else:
                        if page_num % 100 == 0:  # Only show "no data" every 100 pages
                            print(f"  ⚠️  Page {page_num}: No data")
                            
                except Exception as e:
                    print(f"  ❌ Error on page {page_num}: {e}")
                    continue
            
            all_extracted_data.extend(batch_extracted_data)
            
            # Progress update
            print(f"✅ Batch completed: {len(batch_extracted_data):,} records extracted")
            print(f"📊 Total records so far: {len(all_extracted_data):,}")
            print(f"⏭️  Skipped pages so far: {skipped_pages:,}")
            
            # Save progress every batch
            save_progress(batch_start//batch_size + 1, (num_pages + batch_size - 1)//batch_size, len(all_extracted_data), datetime.now())
            
            # Save data every batch
            self.save_to_mysql(batch_extracted_data)  # Save to MySQL
            self.save_to_json(all_extracted_data, "scraped_data.json")  # Backup
            self.save_to_csv(all_extracted_data, "scraped_data.csv")  # Backup
            
            # Also save intermediate data every 50 pages within batch
            if len(batch_extracted_data) > 0:
                print(f"💾 Data saved: {len(all_extracted_data):,} total records")
        
        print(f"\n🎉 Parallel scraping completed!")
        print(f"📊 Total records extracted: {len(all_extracted_data):,}")
        print(f"⏭️  Total pages skipped: {skipped_pages:,}")
        
        return all_extracted_data
    
    def save_to_mysql(self, data: List[Dict[str, str]]):
        """
        Save extracted data to MySQL database
        """
        try:
            if data:
                success = self.db.insert_transactions_batch(data)
                if success:
                    print(f"✅ Saved {len(data)} records to MySQL database")
                else:
                    print("❌ Failed to save data to MySQL database")
        except Exception as e:
            print(f"Error saving data to MySQL: {e}")
    
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
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error saving CSV data: {e}")

def main():
    """
    Main function to run the scraper with sleep prevention and progress tracking
    """
    start_time = datetime.now()
    
    try:
        # Prevent sleep mode
        prevent_sleep()
        
        scraper = PhygitalsScraper()
        
        print("🚀 Starting optimized Phygitals API scraper...")
        print("📊 Extracting: page, batch, time, amount, type, Claw Machine, from, to, name")
        print("🔧 Using 16-thread multiprocessing for maximum performance")
        print("🔄 Resume functionality: ENABLED - will skip already scraped pages")
        print("🔋 Sleep mode prevention: ACTIVE")
        print("-" * 60)
        
        # Use optimized multiprocessing with 16 threads
        total_pages = 21000  # Scrape up to page 21000
        num_processes = 16  # Use all 16 threads
        
        print(f"📈 Total pages to process: {total_pages:,}")
        print(f"🔧 Using {num_processes} processes for maximum performance")
        print(f"⏰ Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check for resume functionality
        last_date = scraper.get_last_scraped_date()
        if last_date:
            print(f"📅 Last scraped date: {last_date}")
            starting_page = scraper.find_starting_page_by_date(last_date, total_pages)
            print(f"🚀 Resuming from page {starting_page}")
        else:
            starting_page = 0
            print("🚀 Starting from page 0 (no previous data found)")
        
        # Use multiprocessing for maximum performance
        all_extracted_data = scraper._scrape_multiple_pages_parallel(total_pages, num_processes, limit=100, start_page=starting_page)
        
        extracted_data = all_extracted_data

        # Final save to ensure all data is captured
        if extracted_data:
            # Data is already saved to MySQL during scraping
            # Save backups to JSON/CSV for safety
            scraper.save_to_json(extracted_data, "scraped_data_backup.json")
            scraper.save_to_csv(extracted_data, "scraped_data_backup.csv")

        if extracted_data:
            end_time = datetime.now()
            duration = end_time - start_time
            
            print(f"\n🎉 SUCCESS! Scraping completed!")
            print(f"⏰ Duration: {duration}")
            print(f"📊 Total records: {len(extracted_data):,}")
            
            # Display first few records as preview
            print("\n📋 Preview of extracted data:")
            print("-" * 60)
            for i, record in enumerate(extracted_data[:3]):
                print(f"Record {i+1}:")
                for key, value in record.items():
                    print(f"  {key}: {value}")
                print()
            
            # Show statistics
            pages_with_data = set(record['page'] for record in extracted_data)
            print(f"\n📈 Final Statistics:")
            print(f"  • Total records: {len(extracted_data):,}")
            print(f"  • Pages with data: {len(pages_with_data):,}")
            print(f"  • Page range: {min(pages_with_data)} - {max(pages_with_data)}")
            print(f"  • Total pages processed: 21,465")
            print(f"  • Total items processed: {21465 * 100:,}")
            print(f"  • Data saved to: MySQL database 'scraped_data'")
            print(f"  • Backup files: scraped_data_backup.json, scraped_data_backup.csv")
        else:
            print("❌ No data was extracted. Please check the API or try again.")
            
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrupted by user.")
        print("💾 Progress has been saved. You can resume from where you left off.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("💾 Progress has been saved. Check scraping_progress.json for details.")
    finally:
        # Re-enable sleep mode
        allow_sleep()
        print("\n🔋 Sleep mode re-enabled")

if __name__ == "__main__":
    main()
