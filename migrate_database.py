#!/usr/bin/env python3
"""
Database migration script to add date field and populate it with time data
"""

import sys
import os
from datetime import datetime

# Add the current directory to the path so we can import scraper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_config import DatabaseConfig

def migrate_database():
    """Migrate database to add date field and populate it"""
    print("🔄 Starting Database Migration")
    print("=" * 50)
    
    try:
        db = DatabaseConfig()
        connection = db.get_connection()
        
        if not connection:
            print("❌ Could not connect to database")
            return False
        
        cursor = connection.cursor()
        
        # Check if date column exists
        cursor.execute("DESCRIBE transactions")
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        
        if 'date' not in column_names:
            print("📝 Adding date column to transactions table...")
            cursor.execute("ALTER TABLE transactions ADD COLUMN date VARCHAR(255)")
            print("✅ Date column added")
        else:
            print("✅ Date column already exists")
        
        # Check how many records need date field populated
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE date IS NULL OR date = ''")
        null_date_count = cursor.fetchone()[0]
        
        if null_date_count > 0:
            print(f"📝 Populating date field for {null_date_count} records...")
            
            # Update records where date is null or empty to use time field
            cursor.execute("""
                UPDATE transactions 
                SET date = time 
                WHERE date IS NULL OR date = ''
            """)
            
            connection.commit()
            print(f"✅ Updated {null_date_count} records with date field")
        else:
            print("✅ All records already have date field populated")
        
        # Verify the migration
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE date IS NULL OR date = ''")
        remaining_null = cursor.fetchone()[0]
        
        if remaining_null == 0:
            print("✅ Migration completed successfully!")
        else:
            print(f"⚠️  {remaining_null} records still have null date field")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_migration():
    """Verify that the migration was successful"""
    print("\n🔍 Verifying Migration")
    print("=" * 50)
    
    try:
        db = DatabaseConfig()
        connection = db.get_connection()
        
        if not connection:
            print("❌ Could not connect to database")
            return False
        
        cursor = connection.cursor()
        
        # Check total records
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total_records = cursor.fetchone()[0]
        print(f"📊 Total records: {total_records}")
        
        # Check records with date field
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE date IS NOT NULL AND date != ''")
        records_with_date = cursor.fetchone()[0]
        print(f"📊 Records with date field: {records_with_date}")
        
        # Check records without date field
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE date IS NULL OR date = ''")
        records_without_date = cursor.fetchone()[0]
        print(f"📊 Records without date field: {records_without_date}")
        
        # Sample some records to verify
        cursor.execute("SELECT date, time FROM transactions LIMIT 5")
        samples = cursor.fetchall()
        
        print(f"\n📋 Sample records:")
        for i, (date, time) in enumerate(samples):
            print(f"  {i+1}. Date: {date}, Time: {time}")
        
        cursor.close()
        connection.close()
        
        success = records_without_date == 0
        if success:
            print("✅ Migration verification successful!")
        else:
            print("❌ Migration verification failed - some records still missing date field")
        
        return success
        
    except Exception as e:
        print(f"❌ Migration verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Database Migration Tool")
    print("=" * 70)
    
    # Run migration
    migration_success = migrate_database()
    
    if migration_success:
        # Verify migration
        verification_success = verify_migration()
        
        if verification_success:
            print("\n🎉 Database migration completed successfully!")
            print("✅ All records now have proper date field populated")
        else:
            print("\n⚠️  Migration completed but verification failed")
    else:
        print("\n❌ Database migration failed")
