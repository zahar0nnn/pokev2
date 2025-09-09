#!/usr/bin/env python3
"""
Quick duplicate check without user interaction
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_config import DatabaseConfig

def quick_duplicate_check():
    """Quick check for duplicates"""
    print("🔍 Quick Duplicate Check")
    print("=" * 30)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        db = DatabaseConfig()
        connection = db.get_connection()
        
        if not connection:
            print("❌ Cannot connect to database")
            return False
        
        cursor = connection.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total transactions: {total_count:,}")
        
        # Check for exact duplicates
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT time, amount, type, COUNT(*) as count
                FROM transactions 
                GROUP BY time, amount, type 
                HAVING COUNT(*) > 1
            ) as duplicates
        """)
        duplicate_groups = cursor.fetchone()[0]
        
        if duplicate_groups > 0:
            print(f"❌ Found {duplicate_groups} groups of exact duplicates")
            
            # Get total duplicate records
            cursor.execute("""
                SELECT SUM(count - 1) FROM (
                    SELECT time, amount, type, COUNT(*) as count
                    FROM transactions 
                    GROUP BY time, amount, type 
                    HAVING COUNT(*) > 1
                ) as duplicates
            """)
            duplicate_records = cursor.fetchone()[0] or 0
            print(f"📊 Duplicate records: {duplicate_records:,}")
            print(f"📊 Records to keep: {total_count - duplicate_records:,}")
            
            # Show some examples
            cursor.execute("""
                SELECT time, amount, type, COUNT(*) as count
                FROM transactions 
                GROUP BY time, amount, type 
                HAVING COUNT(*) > 1
                ORDER BY count DESC
                LIMIT 5
            """)
            examples = cursor.fetchall()
            
            print(f"\n📋 Top duplicate examples:")
            for dup in examples:
                print(f"  {dup[0]} | {dup[1]} | {dup[2]} | Count: {dup[3]}")
            
            return False
        else:
            print("✅ No exact duplicates found")
        
        # Check for empty records
        cursor.execute("""
            SELECT COUNT(*) 
            FROM transactions 
            WHERE time = '' OR amount = '' OR type = '' OR name = ''
        """)
        empty_records = cursor.fetchone()[0]
        
        if empty_records > 0:
            print(f"⚠️  Found {empty_records:,} records with empty fields")
        else:
            print("✅ No empty records found")
        
        # Get date range
        cursor.execute("SELECT MIN(time), MAX(time) FROM transactions WHERE time != ''")
        date_range = cursor.fetchone()
        if date_range[0] and date_range[1]:
            print(f"📅 Date range: {date_range[0]} to {date_range[1]}")
        
        cursor.close()
        connection.close()
        
        if duplicate_groups == 0 and empty_records == 0:
            print("\n🎉 Database is clean!")
            return True
        else:
            print(f"\n⚠️  Database has issues to fix")
            print("💡 Run 'python check_duplicates.py' to clean up")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = quick_duplicate_check()
    sys.exit(0 if success else 1)
