#!/usr/bin/env python3
"""
Optimized monitoring script for the Phygitals scraper
"""

import json
import os
import sys
import requests
from datetime import datetime
from database import Database
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Monitor:
    """Optimized monitoring class"""
    
    def __init__(self):
        try:
            self.db = Database()
            self.db.setup_database()
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            self.db = None
    
    def check_progress_file(self) -> bool:
        """Check progress file"""
        if not os.path.exists('scraping_progress.json'):
            logger.warning("❌ No progress file found")
            return False
        
        try:
            with open('scraping_progress.json', 'r') as f:
                progress = json.load(f)
            
            logger.info("📊 Scraping Progress:")
            logger.info(f"  Current Page: {progress.get('current_page', 'Unknown')}")
            logger.info(f"  Total Pages: {progress.get('total_pages', 'Unknown')}")
            logger.info(f"  Records: {progress.get('records_count', 0):,}")
            logger.info(f"  Progress: {progress.get('progress_percentage', 0):.1f}%")
            logger.info(f"  Last Update: {progress.get('timestamp', 'Unknown')}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Error reading progress file: {e}")
            return False
    
    def check_database(self) -> bool:
        """Check database status"""
        if not self.db:
            logger.error("❌ Database not initialized")
            return False
        
        try:
            stats = self.db.get_stats()
            
            if not stats:
                logger.error("❌ Database connection failed")
                return False
            
            logger.info("🗄️  Database Status:")
            logger.info(f"  Total Records: {stats.get('total_records', 0):,}")
            logger.info(f"  Total Pages: {stats.get('total_pages', 0):,}")
            logger.info(f"  Last Scraped Page: {stats.get('last_scraped_page', 0)}")
            logger.info(f"  Last Scraped Time: {stats.get('last_scraped_time', 'Unknown')}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Database check failed: {e}")
            return False
    
    def check_webapp(self) -> bool:
        """Check webapp status"""
        try:
            response = requests.get("http://localhost:5001/debug", timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Web app is running")
                logger.info(f"  Status: {data.get('status', 'Unknown')}")
                logger.info(f"  Database: {data.get('database', 'Unknown')}")
                return True
            else:
                logger.warning(f"⚠️  Web app returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Web app not accessible: {e}")
            return False
    
    def run_health_check(self) -> bool:
        """Run complete health check"""
        logger.info("🔍 Phygitals Scraper Health Check")
        logger.info("=" * 50)
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("")
        
        # Check progress
        progress_ok = self.check_progress_file()
        logger.info("")
        
        # Check database
        db_ok = self.check_database()
        logger.info("")
        
        # Check webapp
        webapp_ok = self.check_webapp()
        logger.info("")
        
        # Summary
        logger.info("=" * 50)
        logger.info("📊 Summary:")
        logger.info(f"  Progress File: {'✅ OK' if progress_ok else '❌ MISSING'}")
        logger.info(f"  Database: {'✅ OK' if db_ok else '❌ ISSUES'}")
        logger.info(f"  Web App: {'✅ OK' if webapp_ok else '❌ NOT RUNNING'}")
        
        overall_health = progress_ok and db_ok
        
        if overall_health:
            logger.info("\n🎉 Scraper appears to be working!")
        else:
            logger.info("\n⚠️  Some issues detected")
            logger.info("💡 Try running: python scraper.py")
        
        return overall_health

def main():
    """Main function"""
    monitor = Monitor()
    success = monitor.run_health_check()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
