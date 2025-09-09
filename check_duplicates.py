#!/usr/bin/env python3
"""
Check and remove duplicates from the database
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_config import DatabaseConfig

def check_database_connection():
    """Check if database connection works"""
    print("🗄️  Checking Database Connection...")
    print("-" * 35)
    
    try:
        db = DatabaseConfig()
        connection = db.get_connection()
        
        if connection:
            print("✅ Database connection successful")
            return db, connection
        else:
            print("❌ Database connection failed")
            return None, None
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None, None

def analyze_duplicates(db, connection):
    """Analyze duplicates in the database"""
    print("\n🔍 Analyzing Duplicates...")
    print("-" * 30)
    
    cursor = connection.cursor()
    
    try:
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total transactions: {total_count:,}")
        
        # Check for exact duplicates (same time, amount, type)
        cursor.execute("""
            SELECT time, amount, type, COUNT(*) as count
            FROM transactions 
            GROUP BY time, amount, type 
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)
        exact_duplicates = cursor.fetchall()
        
        if exact_duplicates:
            print(f"\n❌ Found {len(exact_duplicates)} groups of exact duplicates:")
            total_duplicate_records = 0
            for dup in exact_duplicates:
                print(f"  {dup[0]} | {dup[1]} | {dup[2]} | Count: {dup[3]}")
                total_duplicate_records += dup[3] - 1  # -1 because we keep one
            
            print(f"\n📊 Duplicate records to remove: {total_duplicate_records:,}")
            print(f"📊 Records to keep: {total_count - total_duplicate_records:,}")
        else:
            print("✅ No exact duplicates found")
        
        # Check for similar duplicates (same time and amount, different type)
        cursor.execute("""
            SELECT time, amount, COUNT(*) as count
            FROM transactions 
            GROUP BY time, amount 
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            LIMIT 10
        """)
        similar_duplicates = cursor.fetchall()
        
        if similar_duplicates:
            print(f"\n⚠️  Found {len(similar_duplicates)} groups of similar duplicates (same time+amount):")
            for dup in similar_duplicates:
                print(f"  {dup[0]} | {dup[1]} | Count: {dup[2]}")
        else:
            print("✅ No similar duplicates found")
        
        # Check for empty or invalid records
        cursor.execute("""
            SELECT COUNT(*) 
            FROM transactions 
            WHERE time = '' OR amount = '' OR type = '' OR name = ''
        """)
        empty_records = cursor.fetchone()[0]
        
        if empty_records > 0:
            print(f"\n⚠️  Found {empty_records:,} records with empty fields")
        else:
            print("✅ No empty records found")
        
        return exact_duplicates, similar_duplicates, empty_records
        
    except Exception as e:
        print(f"❌ Error analyzing duplicates: {e}")
        return [], [], 0
    finally:
        cursor.close()

def remove_exact_duplicates(db, connection):
    """Remove exact duplicates, keeping the one with highest ID"""
    print("\n🧹 Removing Exact Duplicates...")
    print("-" * 35)
    
    cursor = connection.cursor()
    
    try:
        # Count duplicates before removal
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT time, amount, type, COUNT(*) as count
                FROM transactions 
                GROUP BY time, amount, type 
                HAVING COUNT(*) > 1
            ) as duplicates
        """)
        duplicate_groups = cursor.fetchone()[0]
        
        if duplicate_groups == 0:
            print("✅ No exact duplicates to remove")
            return 0
        
        print(f"📊 Found {duplicate_groups} groups of exact duplicates")
        
        # Remove duplicates, keeping the one with the highest ID
        cursor.execute("""
            DELETE t1 FROM transactions t1
            INNER JOIN transactions t2 
            WHERE t1.id < t2.id 
            AND t1.time = t2.time 
            AND t1.amount = t2.amount 
            AND t1.type = t2.type
        """)
        
        removed_count = cursor.rowcount
        connection.commit()
        
        print(f"✅ Removed {removed_count:,} duplicate transactions")
        print(f"✅ Kept the most recent record from each duplicate group")
        
        return removed_count
        
    except Exception as e:
        print(f"❌ Error removing duplicates: {e}")
        connection.rollback()
        return 0
    finally:
        cursor.close()

def remove_empty_records(db, connection):
    """Remove records with empty required fields"""
    print("\n🧹 Removing Empty Records...")
    print("-" * 30)
    
    cursor = connection.cursor()
    
    try:
        # Count empty records
        cursor.execute("""
            SELECT COUNT(*) 
            FROM transactions 
            WHERE time = '' OR amount = '' OR type = '' OR name = ''
        """)
        empty_count = cursor.fetchone()[0]
        
        if empty_count == 0:
            print("✅ No empty records to remove")
            return 0
        
        print(f"📊 Found {empty_count:,} empty records")
        
        # Remove empty records
        cursor.execute("""
            DELETE FROM transactions 
            WHERE time = '' OR amount = '' OR type = '' OR name = ''
        """)
        
        removed_count = cursor.rowcount
        connection.commit()
        
        print(f"✅ Removed {removed_count:,} empty records")
        
        return removed_count
        
    except Exception as e:
        print(f"❌ Error removing empty records: {e}")
        connection.rollback()
        return 0
    finally:
        cursor.close()

def optimize_database(db, connection):
    """Optimize database tables"""
    print("\n⚡ Optimizing Database...")
    print("-" * 25)
    
    cursor = connection.cursor()
    
    try:
        # Analyze tables
        print("  Analyzing tables...")
        cursor.execute("ANALYZE TABLE transactions")
        cursor.execute("ANALYZE TABLE scraped_pages")
        
        # Optimize tables
        print("  Optimizing tables...")
        cursor.execute("OPTIMIZE TABLE transactions")
        cursor.execute("OPTIMIZE TABLE scraped_pages")
        
        connection.commit()
        print("  ✅ Database optimized")
        
        return True
        
    except Exception as e:
        print(f"❌ Error optimizing database: {e}")
        return False
    finally:
        cursor.close()

def get_final_stats(db, connection):
    """Get final database statistics"""
    print("\n📊 Final Database Statistics...")
    print("-" * 35)
    
    cursor = connection.cursor()
    
    try:
        # Get final count
        cursor.execute("SELECT COUNT(*) FROM transactions")
        final_count = cursor.fetchone()[0]
        
        # Get date range
        cursor.execute("SELECT MIN(time), MAX(time) FROM transactions WHERE time != ''")
        date_range = cursor.fetchone()
        
        # Get page range
        cursor.execute("SELECT MIN(page_number), MAX(page_number) FROM transactions")
        page_range = cursor.fetchone()
        
        print(f"📊 Total transactions: {final_count:,}")
        
        if date_range[0] and date_range[1]:
            print(f"📅 Date range: {date_range[0]} to {date_range[1]}")
        
        if page_range[0] is not None and page_range[1] is not None:
            print(f"📄 Page range: {page_range[0]:,} to {page_range[1]:,}")
        
        return final_count
        
    except Exception as e:
        print(f"❌ Error getting final stats: {e}")
        return 0
    finally:
        cursor.close()

def main():
    """Main function"""
    print("🔍 Database Duplicate Checker")
    print("=" * 40)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check database connection
    db, connection = check_database_connection()
    if not db or not connection:
        print("\n❌ Cannot connect to database")
        return False
    
    try:
        # Analyze duplicates
        exact_duplicates, similar_duplicates, empty_records = analyze_duplicates(db, connection)
        
        # Ask user if they want to proceed
        if exact_duplicates or empty_records:
            print(f"\n❓ Found issues to fix:")
            if exact_duplicates:
                print(f"  - {len(exact_duplicates)} groups of exact duplicates")
            if empty_records:
                print(f"  - {empty_records:,} empty records")
            
            response = input("\n🤔 Do you want to clean up these issues? (y/n): ").lower().strip()
            
            if response == 'y' or response == 'yes':
                # Remove duplicates
                removed_duplicates = remove_exact_duplicates(db, connection)
                
                # Remove empty records
                removed_empty = remove_empty_records(db, connection)
                
                # Optimize database
                optimize_database(db, connection)
                
                # Get final stats
                final_count = get_final_stats(db, connection)
                
                print("\n" + "=" * 40)
                print("🎉 CLEANUP COMPLETED!")
                print("=" * 40)
                print(f"✅ Removed {removed_duplicates:,} duplicate transactions")
                print(f"✅ Removed {removed_empty:,} empty records")
                print(f"✅ Final count: {final_count:,} transactions")
                print("✅ Database optimized")
            else:
                print("\n⏭️  Skipping cleanup")
        else:
            print("\n✅ No issues found - database is clean!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        return False
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
