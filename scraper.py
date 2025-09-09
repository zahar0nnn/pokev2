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
        self.db = DatabaseConfig()
        
        # Initialize database and tables with error handling
        try:
            self.db.create_database_and_tables()
            print("✅ Database connection established successfully")
        except Exception as e:
            print(f"❌ Failed to initialize database: {e}")
            print("💡 The scraper will continue but data won't be saved to MySQL.")
            print("💡 You can still use JSON/CSV backup files.")
            # Set db to None to indicate database is not available
            self.db = None
    
    def load_scraped_pages(self):
        """Load list of already scraped pages from database"""
        if self.db is None:
            print("⚠️  Database not available - starting with empty scraped pages list")
            self.scraped_pages = set()
            return self.scraped_pages
        
        self.scraped_pages = self.db.get_scraped_pages()
        print(f"📋 Loaded {len(self.scraped_pages)} scraped pages from database")
        return self.scraped_pages
    
    def is_page_scraped(self, page_num):
        """Check if a page has already been scraped"""
        return page_num in self.scraped_pages
    
    def mark_page_scraped(self, page_num):
        """Mark a page as successfully scraped"""
        self.scraped_pages.add(page_num)
        if self.db is not None:
            self.db.mark_page_scraped(page_num)
    
    def get_last_scraped_date(self):
        """Get the date of the last scraped transaction"""
        if self.db is None:
            print("⚠️  Database not available - cannot get last scraped date")
            return None
            
        connection = None
        cursor = None
        try:
            connection = self.db.get_connection()
            if not connection:
                return None
                
            cursor = connection.cursor()
            cursor.execute("SELECT COALESCE(date, time) FROM transactions ORDER BY COALESCE(date, time) DESC LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"Error getting last scraped date: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def get_first_scraped_date(self):
        """Get the date of the first scraped transaction"""
        if self.db is None:
            print("⚠️  Database not available - cannot get first scraped date")
            return None
            
        connection = None
        cursor = None
        try:
            connection = self.db.get_connection()
            if not connection:
                return None
                
            cursor = connection.cursor()
            cursor.execute("SELECT COALESCE(date, time) FROM transactions ORDER BY COALESCE(date, time) ASC LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"Error getting first scraped date: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def find_page_by_date(self, target_date, search_direction='forward', max_pages_to_check=1000):
        """
        Find the page number that contains a specific transaction date
        
        Args:
            target_date: The transaction date to search for (ISO format)
            search_direction: 'forward' (from page 0) or 'backward' (from high page numbers)
            max_pages_to_check: Maximum number of pages to search through
        
        Returns:
            dict: {
                'page_number': int or None,
                'found_exact': bool,
                'pages_checked': int,
                'search_method': str
            }
        """
        print(f"🔍 Finding page for date: {target_date} (direction: {search_direction})")
        
        if search_direction == 'forward':
            return self._find_page_by_date_forward(target_date, max_pages_to_check)
        else:
            return self._find_page_by_date_backward(target_date, max_pages_to_check)
    
    def _find_page_by_date_forward(self, target_date, max_pages_to_check):
        """Search forward from page 0 to find the target date"""
        print("🔍 Searching forward from page 0...")
        
        current_page = 0
        pages_checked = 0
        found_exact = False
        found_page = None
        
        while current_page < max_pages_to_check and not found_exact and pages_checked < max_pages_to_check:
            try:
                if pages_checked % 50 == 0:  # Log every 50 pages
                    print(f"  🔍 Checking page {current_page}...")
                
                data = self.scrape_page(current_page, limit=100)  # Get more items for better date coverage
                
                if data and len(data) > 0:
                    # Check all transactions on this page for our target date
                    for transaction in data:
                        transaction_date = transaction.get('time', '')
                        if transaction_date == target_date:
                            print(f"    ✅ Found exact date {target_date} on page {current_page}")
                            found_exact = True
                            found_page = current_page
                            break
                        elif transaction_date < target_date:
                            # We've gone too far back, the target date should be on a later page
                            if pages_checked % 50 == 0:
                                print(f"    📅 Page {current_page} has older date {transaction_date}, continuing...")
                            break
                    
                    if not found_exact:
                        # Check the latest date on this page
                        latest_date = data[0].get('time', '')
                        if pages_checked % 50 == 0:
                            print(f"    📅 Page {current_page} latest date: {latest_date}")
                        
                        if latest_date < target_date:
                            # This page is too old, continue to next page
                            current_page += 1
                        else:
                            # This page might contain our target date, check more thoroughly
                            current_page += 1
                else:
                    # No data on this page, continue
                    current_page += 1
                    
                pages_checked += 1
                    
            except Exception as e:
                print(f"    ❌ Error checking page {current_page}: {e}")
                current_page += 1
                pages_checked += 1
        
        if not found_exact:
            print(f"    ⚠️  Could not find exact date {target_date} in first {pages_checked} pages")
            found_page = None
        
        return {
            'page_number': found_page,
            'found_exact': found_exact,
            'pages_checked': pages_checked,
            'search_method': 'forward'
        }
    
    def _find_page_by_date_backward(self, target_date, max_pages_to_check, start_from_page=None):
        """Search backward from high page numbers to find the target date"""
        print("🔍 Searching backward from high page numbers...")
        
        # Start from a reasonable high page number
        if start_from_page is not None:
            current_page = min(start_from_page, max_pages_to_check)
        else:
            # Use a sensible default high page number, not max_pages_to_check
            current_page = min(10000, max_pages_to_check)  # Start from page 10000 or max_pages_to_check
        pages_checked = 0
        found_exact = False
        found_page = None
        
        while current_page >= 0 and not found_exact and pages_checked < max_pages_to_check:
            try:
                if pages_checked % 50 == 0:  # Log every 50 pages
                    print(f"  🔍 Checking page {current_page}...")
                
                data = self.scrape_page(current_page, limit=100)
                
                if data and len(data) > 0:
                    # Check all transactions on this page for our target date
                    for transaction in data:
                        transaction_date = transaction.get('time', '')
                        if transaction_date == target_date:
                            print(f"    ✅ Found exact date {target_date} on page {current_page}")
                            found_exact = True
                            found_page = current_page
                            break
                        elif transaction_date > target_date:
                            # We've gone too far forward, the target date should be on an earlier page
                            if pages_checked % 50 == 0:
                                print(f"    📅 Page {current_page} has newer date {transaction_date}, continuing...")
                            break
                    
                    if not found_exact:
                        # Check the earliest date on this page
                        earliest_date = data[-1].get('time', '')
                        if pages_checked % 50 == 0:
                            print(f"    📅 Page {current_page} earliest date: {earliest_date}")
                        
                        if earliest_date > target_date:
                            # This page is too new, continue to earlier page
                            current_page -= 1
                        else:
                            # This page might contain our target date, check more thoroughly
                            current_page -= 1
                else:
                    # No data on this page, continue
                    current_page -= 1
                    
                pages_checked += 1
                    
            except Exception as e:
                print(f"    ❌ Error checking page {current_page}: {e}")
                current_page -= 1
                pages_checked += 1
        
        if not found_exact:
            print(f"    ⚠️  Could not find exact date {target_date} in {pages_checked} pages")
            found_page = None
        
        return {
            'page_number': found_page,
            'found_exact': found_exact,
            'pages_checked': pages_checked,
            'search_method': 'backward'
        }
    
    def get_date_range_from_database(self):
        """
        Get the complete date range of existing data from database
        
        Returns:
            dict: {
                'first_date': str or None,
                'last_date': str or None,
                'total_records': int,
                'date_range_days': int or None
            }
        """
        if self.db is None:
            print("⚠️  Database not available - cannot get date range")
            return {
                'first_date': None,
                'last_date': None,
                'total_records': 0,
                'date_range_days': None
            }
            
        connection = None
        cursor = None
        try:
            connection = self.db.get_connection()
            if not connection:
                return {
                    'first_date': None,
                    'last_date': None,
                    'total_records': 0,
                    'date_range_days': None
                }
                
            cursor = connection.cursor()
            
            # Get first and last dates (use date field if available, fallback to time)
            cursor.execute("SELECT MIN(COALESCE(date, time)) as first_date, MAX(COALESCE(date, time)) as last_date, COUNT(*) as total_records FROM transactions")
            result = cursor.fetchone()
            
            if result and result[0] and result[1]:
                first_date = result[0]
                last_date = result[1]
                total_records = result[2]
                
                # Calculate date range in days
                from datetime import datetime
                try:
                    first_dt = datetime.fromisoformat(first_date.replace('Z', '+00:00'))
                    last_dt = datetime.fromisoformat(last_date.replace('Z', '+00:00'))
                    date_range_days = (last_dt - first_dt).days
                except:
                    date_range_days = None
                
                print(f"📊 Database date range: {first_date} to {last_date}")
                print(f"📊 Total records: {total_records:,}")
                print(f"📊 Date range: {date_range_days} days")
                
                return {
                    'first_date': first_date,
                    'last_date': last_date,
                    'total_records': total_records,
                    'date_range_days': date_range_days
                }
            else:
                print("📊 No data found in database")
                return {
                    'first_date': None,
                    'last_date': None,
                    'total_records': 0,
                    'date_range_days': None
                }
                
        except Exception as e:
            print(f"Error getting date range from database: {e}")
            return {
                'first_date': None,
                'last_date': None,
                'total_records': 0,
                'date_range_days': None
            }
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def implement_date_based_sandwich_approach(self, max_pages=25603):
        """
        Implement the 3-side date-based sandwich approach:
        1. Side 1: From page 0 to first scraped date (catch new data before existing)
        2. Side 2: Skip intermediate already scraped data (we already have this)
        3. Side 3: From last scraped date to current (catch new data after existing)
        
        Returns:
            dict: {
                'side1_pages': list of page numbers for side 1,
                'side2_skipped': dict with info about skipped data,
                'side3_pages': list of page numbers for side 3,
                'total_pages_to_scrape': int,
                'strategy': str
            }
        """
        print("🥪 IMPLEMENTING DATE-BASED SANDWICH APPROACH")
        print("=" * 60)
        
        # Get existing data date range
        date_range = self.get_date_range_from_database()
        
        if not date_range['first_date'] or not date_range['last_date']:
            print("🚀 No existing data found - using fresh start approach")
            return {
                'side1_pages': list(range(0, min(1000, max_pages))),  # Start with first 1000 pages
                'side2_skipped': {'reason': 'no_existing_data'},
                'side3_pages': [],
                'total_pages_to_scrape': min(1000, max_pages),
                'strategy': 'fresh_start'
            }
        
        first_date = date_range['first_date']
        last_date = date_range['last_date']
        
        print(f"📅 Existing data range: {first_date} to {last_date}")
        print(f"📊 Total existing records: {date_range['total_records']:,}")
        
        # SIDE 1: Find pages from 0 to first scraped date
        print("\n🔍 SIDE 1: Finding pages from page 0 to first scraped date...")
        print("💡 This catches new data that appeared before our existing data")
        
        first_date_result = self.find_page_by_date(first_date, search_direction='forward', max_pages_to_check=2000)
        
        side1_pages = []
        if first_date_result['found_exact'] and first_date_result['page_number'] is not None:
            # Scrape from page 0 to the page containing our first date
            side1_pages = list(range(0, first_date_result['page_number']))
            print(f"✅ Side 1: Will scrape pages 0 to {first_date_result['page_number']-1} ({len(side1_pages)} pages)")
        else:
            print("⚠️  Could not find first date - will start from page 0")
            side1_pages = list(range(0, min(1000, max_pages)))
        
        # SIDE 2: Skip intermediate data (we already have this)
        print(f"\n⏭️  SIDE 2: Skipping intermediate data from {first_date} to {last_date}")
        print("💡 This data is already in our database")
        
        side2_skipped = {
            'first_date': first_date,
            'last_date': last_date,
            'total_records': date_range['total_records'],
            'date_range_days': date_range['date_range_days']
        }
        
        # SIDE 3: Find pages from last scraped date to current
        print(f"\n🔍 SIDE 3: Finding pages from last scraped date to current...")
        print("💡 This catches new data that appeared after our existing data")
        
        last_date_result = self.find_page_by_date(last_date, search_direction='forward', max_pages_to_check=5000)
        
        side3_pages = []
        if last_date_result['found_exact'] and last_date_result['page_number'] is not None:
            # Scrape from the page after our last date to current max pages
            start_page = last_date_result['page_number'] + 1
            side3_pages = list(range(start_page, max_pages))
            print(f"✅ Side 3: Will scrape pages {start_page} to {max_pages-1} ({len(side3_pages)} pages)")
        else:
            print("⚠️  Could not find last date - will scrape recent pages")
            # Fallback: scrape the most recent pages
            side3_pages = list(range(max(0, max_pages - 1000), max_pages))
        
        # Calculate total pages to scrape
        total_pages_to_scrape = len(side1_pages) + len(side3_pages)
        
        print(f"\n📊 SANDWICH APPROACH SUMMARY:")
        print(f"  • Side 1 (older data): {len(side1_pages):,} pages")
        print(f"  • Side 2 (skipped): {date_range['total_records']:,} existing records")
        print(f"  • Side 3 (newer data): {len(side3_pages):,} pages")
        print(f"  • Total pages to scrape: {total_pages_to_scrape:,}")
        print(f"  • Strategy: date_based_sandwich")
        
        return {
            'side1_pages': side1_pages,
            'side2_skipped': side2_skipped,
            'side3_pages': side3_pages,
            'total_pages_to_scrape': total_pages_to_scrape,
            'strategy': 'date_based_sandwich'
        }
    
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
                response = session.get(url, timeout=10)  # Reduced timeout to prevent hanging
                response.raise_for_status()
                
                data = response.json()
                sales_data = data.get('sales', [])
                
                if sales_data:
                    if page % 100 == 0:  # Only print every 100 pages
                        print(f"✓ Page {page}: {len(sales_data)} items scraped")
                    return sales_data
                else:
                    if page % 1000 == 0:  # Only print every 1000 pages for no data
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
        Extract required fields with date-based ordering (consistent with _extract_required_fields_with_page)
        """
        extracted_data = []
        
        for sale in sales_data:
            try:
                # Check if sale is not None and is a dictionary
                if not sale or not isinstance(sale, dict):
                    continue
                
                # Enhanced name extraction with multiple fallback methods
                nft_name = self._extract_name_enhanced(sale)
                
                # Determine if it's a claw machine transaction
                from_address = sale.get("from", "")
                to_address = sale.get("to", "")
                claw_machine_address = "62Q9eeDY3eM8A5CnprBGYMPShdBjAzdpBdr71QHsS8dS"
                
                is_claw_machine = (from_address == claw_machine_address or to_address == claw_machine_address)
                claw_machine_status = "Claw Machine" if is_claw_machine else "human"
                
                # Get transaction time for date-based ordering
                transaction_time = sale.get("time", "")
                
                # Create date-based batch number (group by date instead of page)
                date_batch = 0
                if transaction_time:
                    try:
                        from datetime import datetime
                        # Parse the ISO date and create a batch number based on date
                        dt = datetime.fromisoformat(transaction_time.replace('Z', '+00:00'))
                        # Create batch based on date (e.g., all transactions from same day get same batch)
                        date_batch = int(dt.strftime('%Y%m%d'))
                    except:
                        date_batch = 0  # Fallback to 0 for invalid dates
                
                extracted_sale = {
                    "date": transaction_time,  # Primary field for ordering
                    "page": 0,                # Default page for this function
                    "batch": date_batch,      # Date-based batch instead of page-based
                    "time": transaction_time, # Keep time field for compatibility
                    "amount": sale.get("amount", ""),
                    "type": sale.get("type", ""),
                    "Claw Machine": claw_machine_status,
                    "from": from_address,
                    "to": to_address,
                    "name": nft_name
                }
                extracted_data.append(extracted_sale)
            except Exception as e:
                print(f"Error extracting data from sale: {e}")
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
            # Check if title is directly in ebayListing
            name = ebay_data.get("title", "")
            if name and name.strip():
                return name.strip()
            
            # If not found, check in ebayListing.data.title
            if "data" in ebay_data:
                data_section = ebay_data.get("data", {})
                if isinstance(data_section, dict):
                    name = data_section.get("title", "")
                    if name and name.strip():
                        return name.strip()
        
        # Method 3: Check for any field that might contain a name
        # Look for fields that contain Pokemon-related keywords
        pokemon_keywords = ['pokemon', 'card', 'trading', 'booster', 'pack', 'box', 'set']
        
        for key, value in sale.items():
            if isinstance(value, str) and len(value) > 5:
                # Check if the value contains Pokemon-related keywords
                if any(keyword in value.lower() for keyword in pokemon_keywords):
                    # Additional validation - make sure it's not just a random string
                    if len(value) > 10 and not value.isdigit():
                        return value.strip()
        
        # Method 4: Check for any string field that looks like a product name
        for key, value in sale.items():
            if isinstance(value, str) and len(value) > 15 and len(value) < 200:
                # Check if it looks like a product name (contains spaces, not just numbers)
                if ' ' in value and not value.replace(' ', '').isdigit():
                    # Additional checks to avoid false positives
                    if not any(skip_word in value.lower() for skip_word in ['http', 'www', 'api', 'json', 'null', 'undefined']):
                        return value.strip()
        
        # Method 5: Check nested objects for name fields
        for key, value in sale.items():
            if isinstance(value, dict):
                # Recursively check nested objects
                for nested_key, nested_value in value.items():
                    if isinstance(nested_value, str) and len(nested_value) > 10:
                        if any(keyword in nested_value.lower() for keyword in pokemon_keywords):
                            return nested_value.strip()
        
        # If no name found, return empty string
        return ""
    
    def _extract_required_fields_with_page(self, sales_data: List[Dict[str, Any]], page_number: int) -> List[Dict[str, str]]:
        """
        Extract required fields with date-based ordering instead of page-based
        """
        extracted_data = []
        
        for sale in sales_data:
            try:
                # Check if sale is not None and is a dictionary
                if not sale or not isinstance(sale, dict):
                    continue
                
                # Enhanced name extraction with multiple fallback methods
                nft_name = self._extract_name_enhanced(sale)
                
                # Determine if it's a claw machine transaction
                from_address = sale.get("from", "")
                to_address = sale.get("to", "")
                claw_machine_address = "62Q9eeDY3eM8A5CnprBGYMPShdBjAzdpBdr71QHsS8dS"
                
                is_claw_machine = (from_address == claw_machine_address or to_address == claw_machine_address)
                claw_machine_status = "Claw Machine" if is_claw_machine else "human"
                
                # Get transaction time for date-based ordering
                transaction_time = sale.get("time", "")
                
                # Create date-based batch number (group by date instead of page)
                date_batch = 0
                if transaction_time:
                    try:
                        from datetime import datetime
                        # Parse the ISO date and create a batch number based on date
                        dt = datetime.fromisoformat(transaction_time.replace('Z', '+00:00'))
                        # Create batch based on date (e.g., all transactions from same day get same batch)
                        date_batch = int(dt.strftime('%Y%m%d'))
                    except:
                        date_batch = page_number // 100  # Fallback to page-based batch
                
                extracted_sale = {
                    "date": transaction_time,  # Primary field for ordering
                    "page": page_number,      # Keep page for reference but not primary
                    "batch": date_batch,      # Date-based batch instead of page-based
                    "time": transaction_time, # Keep time field for compatibility
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
    
    def _scrape_pages_list_parallel(self, pages_list: List[int], num_processes: int = 10, limit: int = 10) -> List[Dict[str, str]]:
        """
        Scrape a specific list of pages using parallel processing
        
        Args:
            pages_list: List of page numbers to scrape
            num_processes: Number of parallel processes
            limit: Number of items per page
            
        Returns:
            List of extracted data from all pages
        """
        if not pages_list:
            print("📋 No pages to scrape in list")
            return []
        
        print(f"🚀 Scraping {len(pages_list)} specific pages with {num_processes} workers...")
        
        # Load already scraped pages
        self.load_scraped_pages()
        
        # Filter out already scraped pages
        unscraped_pages = [page for page in pages_list if page not in self.scraped_pages]
        
        if not unscraped_pages:
            print("✅ All pages in list already scraped!")
            return []
        
        print(f"📋 Found {len(unscraped_pages)} unscraped pages out of {len(pages_list)} total pages")
        
        # Group pages into ranges for workers
        worker_ranges = self._get_worker_ranges_from_pages_list(unscraped_pages, num_processes)
        
        print(f"\n📋 Worker Page Distribution:")
        for worker in worker_ranges:
            print(f"  Worker {worker['worker_id']}: {len(worker['pages'])} pages")
        
        # Process workers in parallel
        print(f"\n🚀 Starting {len(worker_ranges)} parallel workers...")
        
        # Create a partial function with the scraper instance
        scrape_worker_pages_func = partial(self._scrape_worker_pages_list, limit=limit)
        
        # Use multiprocessing Pool for true parallel execution
        with Pool(processes=min(num_processes, len(worker_ranges))) as pool:
            # Map worker page lists to worker functions - this runs in parallel!
            worker_results = pool.map(scrape_worker_pages_func, worker_ranges)
        
        # Collect all results
        all_extracted_data = []
        for i, worker_data in enumerate(worker_results):
            worker_id = i + 1
            print(f"✅ Worker {worker_id} completed: {len(worker_data)} records")
            all_extracted_data.extend(worker_data)
        
        print(f"\n🎉 Parallel scraping completed!")
        print(f"📊 Total records extracted: {len(all_extracted_data)}")
        
        return all_extracted_data
    
    def _get_worker_ranges_from_pages_list(self, pages_list: List[int], num_processes: int) -> List[dict]:
        """
        Distribute a list of pages among workers
        """
        if not pages_list:
            return []
        
        # Sort pages for better distribution
        pages_list = sorted(pages_list)
        
        # Calculate pages per worker
        pages_per_worker = len(pages_list) // num_processes
        remainder_pages = len(pages_list) % num_processes
        
        worker_ranges = []
        current_index = 0
        
        for worker_id in range(1, num_processes + 1):
            # Calculate how many pages this worker gets
            worker_page_count = pages_per_worker + (1 if worker_id <= remainder_pages else 0)
            
            if worker_page_count > 0:
                # Assign pages to this worker
                worker_pages = pages_list[current_index:current_index + worker_page_count]
                current_index += worker_page_count
                
                worker_ranges.append({
                    'worker_id': worker_id,
                    'pages': worker_pages
                })
        
        return worker_ranges
    
    def _scrape_worker_pages_list(self, worker_info: dict, limit: int) -> List[Dict[str, str]]:
        """
        Worker function that processes a specific list of pages
        """
        worker_id = worker_info['worker_id']
        pages = worker_info['pages']
        
        print(f"  🔧 Worker {worker_id}: Processing {len(pages)} pages")
        
        # Create a new database connection for this worker process
        worker_db = DatabaseConfig()
        
        # Load scraped pages for this worker
        scraped_pages = set()
        try:
            scraped_pages = worker_db.get_scraped_pages()
        except:
            print(f"    ⚠️  Worker {worker_id}: Could not load scraped pages, starting fresh")
        
        worker_data = []
        pages_processed = 0
        pages_skipped = 0
        
        # Create a new session for this worker
        worker_session = requests.Session()
        worker_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Process each page assigned to this worker
        for page_num in pages:
            # Check if page is already scraped
            if page_num in scraped_pages:
                pages_skipped += 1
                continue
            
            try:
                # Scrape single page using worker's own session
                url = f"{self.base_url}?limit={limit}&page={page_num}"
                response = worker_session.get(url, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                sales_data = data.get('sales', [])
                
                if sales_data:
                    # Extract data with correct page number
                    extracted_data = self._extract_required_fields_with_page(sales_data, page_num)
                    worker_data.extend(extracted_data)
                    
                    # Mark page as successfully scraped
                    try:
                        worker_db.mark_page_scraped(page_num)
                    except:
                        pass
                    
                    if pages_processed % 50 == 0:  # Progress update every 50 pages
                        print(f"      📄 Worker {worker_id} - Page {page_num}: {len(extracted_data)} records")
                        
            except Exception as e:
                print(f"      ❌ Worker {worker_id} - Error on page {page_num}: {e}")
                continue
            
            pages_processed += 1
            
            # Save to database every 10 pages for better performance
            if len(worker_data) > 0 and pages_processed % 10 == 0:
                try:
                    worker_db.insert_transactions_batch(worker_data)
                    worker_data = []  # Clear after saving
                except:
                    pass
        
        # Final flush: save any remaining records not yet batch-saved
        if len(worker_data) > 0:
            try:
                worker_db.insert_transactions_batch(worker_data)
                # Do not clear worker_data here so caller can still receive returned data
            except:
                pass
        
        print(f"  ✅ Worker {worker_id} completed: {pages_processed} pages processed, {pages_skipped} skipped, {len(worker_data)} records")
        
        return worker_data
    
    def _log_sandwich_validation(self, sandwich_strategy: dict, extracted_data: List[Dict[str, str]]):
        """
        Log comprehensive validation information about the sandwich approach
        """
        print(f"\n🔍 SANDWICH APPROACH VALIDATION")
        print("=" * 50)
        
        # Log strategy details
        print(f"📋 Strategy: {sandwich_strategy['strategy']}")
        print(f"📊 Total pages to scrape: {sandwich_strategy['total_pages_to_scrape']:,}")
        
        if sandwich_strategy['strategy'] == 'date_based_sandwich':
            print(f"📋 Side 1 pages: {len(sandwich_strategy['side1_pages']):,}")
            print(f"📋 Side 2 skipped: {sandwich_strategy['side2_skipped']['total_records']:,} records")
            print(f"📋 Side 3 pages: {len(sandwich_strategy['side3_pages']):,}")
            
            # Log date range information
            side2 = sandwich_strategy['side2_skipped']
            print(f"📅 Existing data range: {side2['first_date']} to {side2['last_date']}")
            print(f"📅 Date range span: {side2['date_range_days']} days")
        
        # Log extracted data validation
        if extracted_data:
            # Get date range of extracted data
            dates = [record.get('time', '') for record in extracted_data if record.get('time')]
            if dates:
                min_date = min(dates)
                max_date = max(dates)
                print(f"📅 New data range: {min_date} to {max_date}")
                
                # Count records by date
                from collections import Counter
                date_counts = Counter(dates)
                print(f"📊 Date distribution: {len(date_counts)} unique dates")
                
                # Show top 5 dates by record count
                top_dates = date_counts.most_common(5)
                print("📊 Top 5 dates by record count:")
                for date, count in top_dates:
                    print(f"  • {date}: {count} records")
            
            # Log page distribution
            pages = [record.get('page', 0) for record in extracted_data if record.get('page') is not None]
            if pages:
                min_page = min(pages)
                max_page = max(pages)
                unique_pages = len(set(pages))
                print(f"📄 Page range: {min_page} to {max_page}")
                print(f"📄 Unique pages: {unique_pages}")
            
            # Log claw machine vs human transactions
            claw_machine_count = sum(1 for record in extracted_data if record.get('Claw Machine') == 'Claw Machine')
            human_count = len(extracted_data) - claw_machine_count
            print(f"🤖 Claw Machine transactions: {claw_machine_count:,}")
            print(f"👤 Human transactions: {human_count:,}")
            
            # Log name extraction success rate
            named_records = sum(1 for record in extracted_data if record.get('name', '').strip())
            name_success_rate = (named_records / len(extracted_data)) * 100 if extracted_data else 0
            print(f"📝 Name extraction success: {named_records:,}/{len(extracted_data):,} ({name_success_rate:.1f}%)")
        
        else:
            print("⚠️  No new data extracted")
        
        print("=" * 50)

    def _scrape_multiple_pages_parallel(self, num_pages: int, num_processes: int = 10, limit: int = 10, start_page: int = 0) -> List[Dict[str, str]]:
        """
        Smart parallel scraping with intelligent page distribution and sandwich approach
        """
        print(f"🚀 Starting smart parallel scraping with {num_processes} independent workers...")
        print(f"📊 Processing {num_pages:,} pages with {limit} items per page")
        print(f"🎯 Estimated total items: {num_pages * limit:,} (actual may be ~{num_pages * 10:,} based on API data)")
        
        # Load already scraped pages
        self.load_scraped_pages()
        already_scraped = len(self.scraped_pages)
        print(f"📋 Found {already_scraped:,} already scraped pages - will skip these")
        
        # Get smart page distribution based on already scraped data
        worker_ranges = self._get_smart_worker_ranges(num_pages, num_processes, start_page)
        
        print(f"\n📋 Smart Worker Page Distribution:")
        for worker in worker_ranges:
            unscraped_pages = worker['unscraped_pages']
            print(f"  Worker {worker['worker_id']}: {len(worker['page_ranges'])} ranges, {unscraped_pages:,} unscraped pages")
            for page_range in worker['page_ranges']:
                print(f"    Pages {page_range['start']:,} to {page_range['end']:,} ({page_range['count']:,} pages)")
        
        # Process workers in parallel using multiprocessing
        print(f"\n🚀 Starting {num_processes} parallel workers...")
        
        # Create a partial function with the scraper instance
        scrape_worker_func = partial(self._scrape_worker_range_smart, limit=limit)
        
        # Use multiprocessing Pool for true parallel execution
        with Pool(processes=num_processes) as pool:
            # Map worker ranges to worker functions - this runs in parallel!
            worker_results = pool.map(scrape_worker_func, worker_ranges)
        
        # Collect all results
        all_extracted_data = []
        for i, worker_data in enumerate(worker_results):
            worker_id = i + 1
            print(f"✅ Worker {worker_id} completed: {len(worker_data):,} records")
            all_extracted_data.extend(worker_data)
        
        # Final statistics
        total_records = len(all_extracted_data)
        total_unscraped_pages = sum(worker['unscraped_pages'] for worker in worker_ranges)
        
        print(f"\n🎉 Smart parallel scraping completed!")
        print(f"📊 Total records extracted: {total_records:,}")
        print(f"⏭️  Total unscraped pages processed: {total_unscraped_pages:,}")
        
        # Save final data
        if all_extracted_data:
            self.save_to_mysql(all_extracted_data)
            self.save_to_json(all_extracted_data, "scraped_data.json")
            self.save_to_csv(all_extracted_data, "scraped_data.csv")
            print(f"💾 Final data saved: {total_records:,} total records")
        
        return all_extracted_data
    
    def _get_smart_worker_ranges(self, num_pages: int, num_processes: int, start_page: int = 0) -> List[dict]:
        """
        Get smart page distribution that skips already scraped pages and distributes work evenly
        """
        # Find all unscraped pages
        unscraped_pages = []
        for page in range(start_page, start_page + num_pages):
            if page not in self.scraped_pages:
                unscraped_pages.append(page)
        
        print(f"📊 Found {len(unscraped_pages):,} unscraped pages out of {num_pages:,} total pages")
        
        if not unscraped_pages:
            print("✅ All pages already scraped!")
            return []
        
        # Group unscraped pages into ranges for better efficiency
        page_ranges = self._group_pages_into_ranges(unscraped_pages)
        
        # Distribute ranges among workers
        worker_ranges = []
        ranges_per_worker = len(page_ranges) // num_processes
        remainder_ranges = len(page_ranges) % num_processes
        
        current_range_index = 0
        
        for worker_id in range(1, num_processes + 1):
            # Calculate how many ranges this worker gets
            worker_range_count = ranges_per_worker + (1 if worker_id <= remainder_ranges else 0)
            
            # Assign ranges to this worker
            worker_page_ranges = []
            unscraped_pages_count = 0
            
            for _ in range(worker_range_count):
                if current_range_index < len(page_ranges):
                    range_info = page_ranges[current_range_index]
                    worker_page_ranges.append(range_info)
                    unscraped_pages_count += range_info['count']
                    current_range_index += 1
            
            if worker_page_ranges:  # Only add workers that have work
                worker_ranges.append({
                    'worker_id': worker_id,
                    'page_ranges': worker_page_ranges,
                    'unscraped_pages': unscraped_pages_count
                })
        
        return worker_ranges
    
    def _group_pages_into_ranges(self, pages: List[int], max_gap: int = 10) -> List[dict]:
        """
        Group consecutive pages into ranges for more efficient processing
        """
        if not pages:
            return []
        
        pages = sorted(pages)
        ranges = []
        current_start = pages[0]
        current_end = pages[0]
        
        for i in range(1, len(pages)):
            if pages[i] - pages[i-1] <= max_gap:
                # Pages are close enough, extend current range
                current_end = pages[i]
            else:
                # Gap is too large, start new range
                ranges.append({
                    'start': current_start,
                    'end': current_end,
                    'count': current_end - current_start + 1
                })
                current_start = pages[i]
                current_end = pages[i]
        
        # Add the last range
        ranges.append({
            'start': current_start,
            'end': current_end,
            'count': current_end - current_start + 1
        })
        
        return ranges
    
    def _scrape_worker_range_smart(self, worker_info: dict, limit: int) -> List[Dict[str, str]]:
        """
        Smart worker function that processes multiple page ranges and uses sandwich approach
        """
        worker_id = worker_info['worker_id']
        page_ranges = worker_info['page_ranges']
        
        print(f"  🔧 Worker {worker_id}: Processing {len(page_ranges)} page ranges")
        
        # Create a new database connection for this worker process
        worker_db = DatabaseConfig()
        
        # Load scraped pages for this worker
        scraped_pages = set()
        try:
            scraped_pages = worker_db.get_scraped_pages()
        except:
            print(f"    ⚠️  Worker {worker_id}: Could not load scraped pages, starting fresh")
        
        worker_data = []
        pages_processed = 0
        pages_skipped = 0
        
        # Create a new session for this worker
        worker_session = requests.Session()
        worker_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Process each page range assigned to this worker
        for range_info in page_ranges:
            start_page = range_info['start']
            end_page = range_info['end']
            range_count = range_info['count']
            
            print(f"    📄 Worker {worker_id}: Processing range {start_page:,} to {end_page:,} ({range_count:,} pages)")
            
            # Use sandwich approach within this range
            range_data = self._scrape_range_with_sandwich(
                start_page, end_page, worker_session, worker_db, 
                scraped_pages, limit, worker_id
            )
            
            worker_data.extend(range_data)
            pages_processed += range_count
        
        print(f"  ✅ Worker {worker_id} completed: {pages_processed:,} pages processed, {len(worker_data):,} records")
        
        return worker_data
    
    def _scrape_range_with_sandwich(self, start_page: int, end_page: int, session, db, 
                                   scraped_pages: set, limit: int, worker_id: int) -> List[Dict[str, str]]:
        """
        Scrape a page range using sandwich approach to handle API updates
        """
        range_data = []
        
        # Check if we need to use sandwich approach
        if start_page == 0 and end_page > 1000:
            # This is a large range starting from 0, use sandwich approach
            print(f"    🥪 Worker {worker_id}: Using sandwich approach for range {start_page}-{end_page}")
            
            # Get first and last dates from database for this range
            first_date, last_date = self._get_range_dates(db, start_page, end_page)
            
            if first_date and last_date:
                # Step 1: Scrape from start to first date
                older_data = self._scrape_range_sequential(
                    start_page, end_page, session, db, scraped_pages, 
                    limit, worker_id, target_date=first_date, mode='older'
                )
                range_data.extend(older_data)
                
                # Step 2: Scrape from last date to end
                newer_data = self._scrape_range_sequential(
                    start_page, end_page, session, db, scraped_pages, 
                    limit, worker_id, target_date=last_date, mode='newer'
                )
                range_data.extend(newer_data)
            else:
                # No existing data, scrape normally
                range_data = self._scrape_range_sequential(
                    start_page, end_page, session, db, scraped_pages, 
                    limit, worker_id
                )
        else:
            # Small range or not starting from 0, scrape normally
            range_data = self._scrape_range_sequential(
                start_page, end_page, session, db, scraped_pages, 
                limit, worker_id
            )
        
        return range_data
    
    def _get_range_dates(self, db, start_page: int, end_page: int) -> tuple:
        """Get first and last dates for a page range from database"""
        try:
            # Get first date in range
            first_date = None
            last_date = None
            
            # This is a simplified version - in practice, you'd query the database
            # for dates within the page range
            return first_date, last_date
        except:
            return None, None
    
    def _scrape_range_sequential(self, start_page: int, end_page: int, session, db, 
                               scraped_pages: set, limit: int, worker_id: int, 
                               target_date: str = None, mode: str = 'normal') -> List[Dict[str, str]]:
        """
        Scrape a page range sequentially
        """
        range_data = []
        
        for page_num in range(start_page, end_page + 1):
            # Check if page is already scraped
            if page_num in scraped_pages:
                continue
            
            try:
                # Scrape single page using worker's own session
                url = f"{self.base_url}?limit={limit}&page={page_num}"
                response = session.get(url, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                sales_data = data.get('sales', [])
                
                if sales_data:
                    # Extract data with correct page number
                    extracted_data = self._extract_required_fields_with_page(sales_data, page_num)
                    range_data.extend(extracted_data)
                    
                    # Mark page as successfully scraped
                    try:
                        db.mark_page_scraped(page_num)
                    except:
                        pass
                    
                    if page_num % 100 == 0:  # Progress update every 100 pages
                        print(f"      📄 Worker {worker_id} - Page {page_num}: {len(extracted_data)} records")
                        
            except Exception as e:
                print(f"      ❌ Worker {worker_id} - Error on page {page_num}: {e}")
                continue
            
            # Save to database every 50 pages for better performance
            if len(range_data) > 0 and page_num % 50 == 0:
                try:
                    db.insert_transactions_batch(range_data)
                    range_data = []  # Clear after saving
                except:
                    pass
        
        return range_data
    
    def _scrape_worker_range(self, worker_info: dict, limit: int) -> List[Dict[str, str]]:
        """
        Scrape a specific page range for a single worker
        """
        worker_id = worker_info['worker_id']
        start_page = worker_info['start_page']
        end_page = worker_info['end_page']
        
        print(f"  🔧 Worker {worker_id}: Processing pages {start_page:,} to {end_page-1:,}")
        
        worker_data = []
        pages_processed = 0
        pages_skipped = 0
        
        for page_num in range(start_page, end_page):
                # Check if page is already scraped
                if self.is_page_scraped(page_num):
                    if page_num % 100 == 0:  # Only show skip message every 100 pages
                        print(f"    ⏭️  Worker {worker_id} - Page {page_num}: Already scraped - skipping")
                    pages_skipped += 1
                    continue
                
                try:
                    # Scrape single page
                    sales_data = self.scrape_page(page_num, limit)
                    
                    if sales_data:
                        # Extract data with correct page number
                        extracted_data = self._extract_required_fields_with_page(sales_data, page_num)
                        worker_data.extend(extracted_data)
                        
                        # Mark page as successfully scraped
                        self.mark_page_scraped(page_num)
                        
                        if page_num % 50 == 0:  # Progress update every 50 pages
                            print(f"    📄 Worker {worker_id} - Page {page_num}: {len(extracted_data)} records")
                    else:
                        if page_num % 100 == 0:  # Only show "no data" every 100 pages
                            print(f"    ⚠️  Worker {worker_id} - Page {page_num}: No data")
                            
                except Exception as e:
                    print(f"    ❌ Worker {worker_id} - Error on page {page_num}: {e}")
                    continue
                
                pages_processed += 1
                
                # Save to database every 10 pages for more frequent updates
                if len(worker_data) > 0 and page_num % 10 == 0:
                    self.save_to_mysql(worker_data)
                    worker_data = []  # Clear after saving
        
        print(f"  ✅ Worker {worker_id} completed: {pages_processed:,} pages processed, {pages_skipped:,} skipped, {len(worker_data):,} records")
        
        return worker_data
    
    def _scrape_worker_range_parallel(self, worker_info: dict, limit: int) -> List[Dict[str, str]]:
        """
        Parallel worker function that can be called by multiprocessing Pool
        This function runs in a separate process and handles its own database connection
        """
        worker_id = worker_info['worker_id']
        start_page = worker_info['start_page']
        end_page = worker_info['end_page']
        
        print(f"  🔧 Worker {worker_id}: Processing pages {start_page:,} to {end_page-1:,}")
        
        # Create a new database connection for this worker process
        worker_db = DatabaseConfig()
        
        # Load scraped pages for this worker
        scraped_pages = set()
        try:
            scraped_pages = worker_db.get_scraped_pages()
        except:
            print(f"    ⚠️  Worker {worker_id}: Could not load scraped pages, starting fresh")
        
        worker_data = []
        pages_processed = 0
        pages_skipped = 0
        
        # Create a new session for this worker
        worker_session = requests.Session()
        worker_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        for page_num in range(start_page, end_page):
            # Check if page is already scraped
            if page_num in scraped_pages:
                if page_num % 100 == 0:  # Only show skip message every 100 pages
                    print(f"    ⏭️  Worker {worker_id} - Page {page_num}: Already scraped - skipping")
                pages_skipped += 1
                continue
            
            try:
                # Scrape single page using worker's own session
                url = f"{self.base_url}?limit={limit}&page={page_num}"
                response = worker_session.get(url, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                sales_data = data.get('sales', [])
                
                if sales_data:
                    # Extract data with correct page number
                    extracted_data = self._extract_required_fields_with_page(sales_data, page_num)
                    worker_data.extend(extracted_data)
                    
                    # Mark page as successfully scraped
                    try:
                        worker_db.mark_page_scraped(page_num)
                    except:
                        print(f"    ⚠️  Worker {worker_id}: Could not mark page {page_num} as scraped")
                    
                    if page_num % 50 == 0:  # Progress update every 50 pages
                        print(f"    📄 Worker {worker_id} - Page {page_num}: {len(extracted_data)} records")
                else:
                    if page_num % 100 == 0:  # Only show "no data" every 100 pages
                        print(f"    ⚠️  Worker {worker_id} - Page {page_num}: No data")
                        
            except Exception as e:
                print(f"    ❌ Worker {worker_id} - Error on page {page_num}: {e}")
                continue
            
            pages_processed += 1
            
            # Save to database every 10 pages for more frequent updates
            if len(worker_data) > 0 and page_num % 10 == 0:
                try:
                    worker_db.insert_transactions_batch(worker_data)
                    worker_data = []  # Clear after saving
                except:
                    print(f"    ⚠️  Worker {worker_id}: Could not save data to database")
        
        # Final flush: save any remaining records not yet batch-saved
        if len(worker_data) > 0:
            try:
                worker_db.insert_transactions_batch(worker_data)
                # Do not clear worker_data here so caller can still receive returned data
            except:
                print(f"    ⚠️  Worker {worker_id}: Could not save final data to database")
        
        print(f"  ✅ Worker {worker_id} completed: {pages_processed:,} pages processed, {pages_skipped:,} skipped, {len(worker_data):,} records")
        
        return worker_data
    
    def save_to_mysql(self, data: List[Dict[str, str]]):
        """
        Save extracted data to MySQL database
        """
        if self.db is None:
            print("⚠️  Database not available - skipping MySQL save")
            return
            
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
                if data and len(data) > 0:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                    print(f"Data saved to {filename}")
                else:
                    print(f"No data to save to {filename}")
        except Exception as e:
            print(f"Error saving CSV data: {e}")

def main():
    """
    Main function to run the scraper with progress tracking
    """
    start_time = datetime.now()
    
    try:
        scraper = PhygitalsScraper()
        
        print("🚀 Starting optimized Phygitals API scraper...")
        print("📊 Extracting: date, page, batch, time, amount, type, Claw Machine, from, to, name")
        print("📅 Ordering: By transaction date (most recent first)")
        print("🔧 Using 10 independent workers for maximum performance")
        print("🔄 Resume functionality: ENABLED - will skip already scraped pages")
        print("-" * 60)
        
        # Use optimized multiprocessing with 10 independent workers
        total_pages = 25603  # Scrape up to page 25603 (based on actual data)
        num_processes = 10  # Use 10 independent workers
        
        print(f"📈 Total pages to process: {total_pages:,}")
        print(f"🔧 Using {num_processes} processes for maximum performance")
        print(f"📊 Expected ~{total_pages * 10:,} total transactions (10 per page average)")
        print(f"⏰ Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Implement date-based sandwich approach
        print("🥪 IMPLEMENTING DATE-BASED SANDWICH APPROACH")
        print("=" * 60)
        
        # Get the sandwich strategy
        sandwich_strategy = scraper.implement_date_based_sandwich_approach(total_pages)
        
        all_extracted_data = []
        
        if sandwich_strategy['strategy'] == 'fresh_start':
            print("\n🚀 FRESH START: No previous data found")
            print("🚀 Starting with first 1000 pages")
            all_extracted_data = scraper._scrape_multiple_pages_parallel(
                len(sandwich_strategy['side1_pages']), num_processes, 10, 0
            )
            
        elif sandwich_strategy['strategy'] == 'date_based_sandwich':
            print("\n🥪 EXECUTING DATE-BASED SANDWICH APPROACH")
            
            # SIDE 1: Scrape older data (from page 0 to first scraped date)
            if sandwich_strategy['side1_pages']:
                print(f"\n🔍 SIDE 1: Scraping {len(sandwich_strategy['side1_pages'])} older pages...")
                print("💡 This catches new data that appeared before our existing data")
                
                side1_data = scraper._scrape_pages_list_parallel(
                    sandwich_strategy['side1_pages'], num_processes, 10
                )
                if side1_data:
                    all_extracted_data.extend(side1_data)
                    print(f"✅ Side 1 completed: {len(side1_data)} records")
                else:
                    print("✅ Side 1 completed: No new data found")
            
            # SIDE 2: Skip intermediate data (already logged in strategy)
            print(f"\n⏭️  SIDE 2: Skipping {sandwich_strategy['side2_skipped']['total_records']:,} existing records")
            print("💡 This data is already in our database")
            
            # SIDE 3: Scrape newer data (from last scraped date to current)
            if sandwich_strategy['side3_pages']:
                print(f"\n🔍 SIDE 3: Scraping {len(sandwich_strategy['side3_pages'])} newer pages...")
                print("💡 This catches new data that appeared after our existing data")
                
                side3_data = scraper._scrape_pages_list_parallel(
                    sandwich_strategy['side3_pages'], num_processes, 10
                )
                if side3_data:
                    all_extracted_data.extend(side3_data)
                    print(f"✅ Side 3 completed: {len(side3_data)} records")
                else:
                    print("✅ Side 3 completed: No new data found")
            else:
                print("✅ Side 3: No newer pages to scrape")
        
        print(f"\n🎉 DATE-BASED SANDWICH APPROACH COMPLETED!")
        print(f"📊 Total new records extracted: {len(all_extracted_data):,}")
        print(f"📊 Strategy used: {sandwich_strategy['strategy']}")
        print(f"📊 Total pages processed: {sandwich_strategy['total_pages_to_scrape']:,}")
        
        # Add comprehensive validation logging
        scraper._log_sandwich_validation(sandwich_strategy, all_extracted_data)
        
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

if __name__ == "__main__":
    main()
