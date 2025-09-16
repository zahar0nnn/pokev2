#!/usr/bin/env python3
"""
Optimized Phygitals scraper with better error handling and performance
"""

import requests
import json
import time
import sys
import os
import signal
from datetime import datetime
from database import Database
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PhygitalsScraper:
    """Optimized scraper with better error handling and performance"""
    
    def __init__(self):
        self.base_url = "https://api.phygitals.com/api/marketplace/sales"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Initialize database
        try:
            self.db = Database()
            self.db.setup_database()
            logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            self.db = None
    
        # Setup signal handlers for graceful shutdown
        self.shutdown_requested = False
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except (OSError, ValueError) as e:
            logger.warning(f"⚠️  Could not setup signal handlers: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info("🛑 Shutdown signal received, stopping gracefully...")
        self.shutdown_requested = True
    
    def scrape_page(self, page_num: int) -> list:
        """Scrape a single page with retry logic"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}?page={page_num}"
                logger.info(f"📄 Scraping page {page_num} (attempt {attempt + 1})")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                transactions = data.get('data', [])
                
                logger.info(f"✅ Page {page_num}: Found {len(transactions)} transactions")
                return transactions
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️  Error scraping page {page_num} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    logger.error(f"❌ Failed to scrape page {page_num} after {max_retries} attempts")
                    return []
            except Exception as e:
                logger.error(f"❌ Unexpected error on page {page_num}: {e}")
                return []
        
        return []
    
    def process_transaction(self, transaction: dict, page_num: int) -> dict:
        """Process a single transaction with validation"""
        try:
            # Extract and validate data
            amount = transaction.get('amount', '')
            time_str = transaction.get('time', '')
            
            # Validate required fields
            if not time_str or not amount:
                logger.warning(f"⚠️  Skipping transaction with missing time or amount")
                return None
            
            # Calculate price
            price = 0
            if amount and str(amount).strip():
                try:
                    amount_int = int(str(amount).strip())
                    if amount_int > 0:
                        price = round(amount_int / 1000000, 2)
                except (ValueError, TypeError):
                    logger.warning(f"⚠️  Invalid amount format: {amount}")
                    return None
            
            # Create processed transaction
            processed = {
                'page': page_num,
                'batch': (page_num - 1) // 100 + 1,
                'time': time_str,
                'amount': str(amount),
                'price': price,
                'type': transaction.get('type', ''),
                'claw_machine': transaction.get('claw_machine', ''),
                'from': transaction.get('from_address', ''),
                'to': transaction.get('to_address', ''),
                'name': transaction.get('name', '')
            }
            
            return processed
            
        except Exception as e:
            logger.error(f"⚠️  Error processing transaction: {e}")
            return None
    
    def save_progress(self, page_num: int, total_pages: int, records_count: int):
        """Save progress to JSON file"""
        try:
            progress = {
                'current_page': page_num,
                'total_pages': total_pages,
                'records_count': records_count,
                'timestamp': datetime.now().isoformat(),
                'progress_percentage': round((page_num / total_pages) * 100, 2) if total_pages > 0 else 0
            }
            
            with open('scraping_progress.json', 'w') as f:
                json.dump(progress, f, indent=2)
            
            logger.info(f"💾 Progress: {page_num}/{total_pages} ({progress['progress_percentage']}%) - {records_count} records")
            
        except Exception as e:
            logger.error(f"⚠️  Could not save progress: {e}")
    
    def run(self, start_page: int = 1, max_pages: int = 1000):
        """Main scraping loop with better error handling"""
        logger.info(f"🚀 Starting scraper from page {start_page} to {max_pages}")
        logger.info("=" * 60)
        
        if not self.db:
            logger.error("❌ Database not available, cannot proceed")
            return
        
        # Get already scraped pages
        scraped_pages = self.db.get_scraped_pages()
        logger.info(f"   Found {len(scraped_pages)} already scraped pages")
        
        total_records = 0
        batch_transactions = []
        batch_size = 100  # Save every 100 transactions
        consecutive_errors = 0
        max_consecutive_errors = 50  # Increased from 5 to 50
        empty_page_gap = 0
        max_empty_gap = 100  # Allow up to 100 consecutive empty pages
        
        try:
            for page_num in range(start_page, max_pages + 1):
                # Check for shutdown signal
                if self.shutdown_requested:
                    logger.info("   Shutdown requested, stopping...")
                    break
                
                # Skip if already scraped
                if page_num in scraped_pages:
                    logger.info(f"⏭️  Page {page_num} already scraped, skipping")
                    continue
                
                # Scrape page
                transactions = self.scrape_page(page_num)
                
                if not transactions:
                    consecutive_errors += 1
                    empty_page_gap += 1
                    logger.warning(f"⚠️  No transactions on page {page_num} (error {consecutive_errors}/{max_consecutive_errors}, gap: {empty_page_gap})")
                    
                    # Only stop if we've hit both thresholds
                    if consecutive_errors >= max_consecutive_errors and empty_page_gap >= max_empty_gap:
                        logger.error(f"❌ Too many consecutive errors ({consecutive_errors}) and large empty gap ({empty_page_gap}), stopping")
                        break
                    
                    time.sleep(5)  # Wait before retrying
                    continue
                
                # Reset error counters on success
                consecutive_errors = 0
                empty_page_gap = 0
                
                # Process transactions
                page_records = 0
                for transaction in transactions:
                    if self.shutdown_requested:
                        break
                    processed = self.process_transaction(transaction, page_num)
                    if processed:
                        batch_transactions.append(processed)
                        total_records += 1
                        page_records += 1
                
                # Check for shutdown before database operations
                if self.shutdown_requested:
                    break
                
                # Save batch to database
                if len(batch_transactions) >= batch_size:
                    logger.info(f"   Saving batch of {len(batch_transactions)} transactions...")
                    if self.db.insert_transactions_batch(batch_transactions):
                        batch_transactions = []
                    else:
                        logger.error("❌ Failed to save batch to database")
                
                # Mark page as scraped
                if self.db.mark_page_scraped(page_num, page_records):
                    logger.info(f"✅ Page {page_num} marked as scraped ({page_records} records)")
                else:
                    logger.error(f"⚠️  Failed to mark page {page_num} as scraped")
                
                # Save progress
                self.save_progress(page_num, max_pages, total_records)
                
                # Rate limiting
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("⏹️  Scraping stopped by user")
        except Exception as e:
            logger.error(f"❌ Scraping failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Save remaining transactions
            if batch_transactions and not self.shutdown_requested:
                logger.info(f"   Saving final batch of {len(batch_transactions)} transactions...")
                self.db.insert_transactions_batch(batch_transactions)
            
            # Show final stats
            stats = self.db.get_stats()
            logger.info(f"✅ Scraping completed!")
            logger.info(f"📊 Total records: {total_records}")
            logger.info(f"📄 Pages scraped: {page_num - start_page + 1}")
            if stats:
                logger.info(f"🗄️  Database stats: {stats.get('total_records', 0)} total records, {stats.get('total_pages', 0)} pages")

def main():
    """Main function with command line argument parsing"""
    logger.info("🔍 Phygitals Scraper")
    logger.info("=" * 30)
    
    # Parse command line arguments
    start_page = 1
    max_pages = 1000
    
    if len(sys.argv) > 1:
        try:
            start_page = int(sys.argv[1])
        except ValueError:
            logger.warning("⚠️  Invalid start page, using 1")
    
    if len(sys.argv) > 2:
        try:
            max_pages = int(sys.argv[2])
        except ValueError:
            logger.warning("⚠️  Invalid max pages, using 1000")
    
    # Create and run scraper
    scraper = PhygitalsScraper()
    scraper.run(start_page, max_pages)

if __name__ == "__main__":
    main()
