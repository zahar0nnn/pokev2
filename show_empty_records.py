#!/usr/bin/env python3
"""
Show examples of empty/incomplete transaction records
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_config import DatabaseConfig

def show_empty_records():
    """Show examples of empty records"""
    print("🔍 Empty Records Analysis")
    print("=" * 35)
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
        
        # Check different types of empty records
        print("\n🔍 Analyzing Empty Records...")
        print("-" * 35)
        
        # Records with empty time
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE time = ''")
        empty_time = cursor.fetchone()[0]
        print(f"📅 Empty time: {empty_time:,} records")
        
        # Records with empty amount
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE amount = ''")
        empty_amount = cursor.fetchone()[0]
        print(f"💰 Empty amount: {empty_amount:,} records")
        
        # Records with empty type
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE type = ''")
        empty_type = cursor.fetchone()[0]
        print(f"🏷️  Empty type: {empty_type:,} records")
        
        # Records with empty name
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE name = ''")
        empty_name = cursor.fetchone()[0]
        print(f"📝 Empty name: {empty_name:,} records")
        
        # Records with empty from_address
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE from_address = ''")
        empty_from = cursor.fetchone()[0]
        print(f"👤 Empty from_address: {empty_from:,} records")
        
        # Records with empty to_address
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE to_address = ''")
        empty_to = cursor.fetchone()[0]
        print(f"👤 Empty to_address: {empty_to:,} records")
        
        # Records with empty claw_machine
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE claw_machine = ''")
        empty_claw = cursor.fetchone()[0]
        print(f"🎮 Empty claw_machine: {empty_claw:,} records")
        
        # Records with empty page_number
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE page_number IS NULL")
        empty_page = cursor.fetchone()[0]
        print(f"📄 Empty page_number: {empty_page:,} records")
        
        print("\n" + "=" * 35)
        print("📋 Examples of Empty Records:")
        print("=" * 35)
        
        # Show examples of records with empty time
        if empty_time > 0:
            print(f"\n📅 Examples of records with empty time ({empty_time:,} total):")
            cursor.execute("""
                SELECT id, time, amount, type, name, from_address, to_address, claw_machine, page_number
                FROM transactions 
                WHERE time = ''
                LIMIT 5
            """)
            examples = cursor.fetchall()
            for ex in examples:
                print(f"  ID: {ex[0]} | Time: '{ex[1]}' | Amount: '{ex[2]}' | Type: '{ex[3]}' | Name: '{ex[4]}'")
        
        # Show examples of records with empty amount
        if empty_amount > 0:
            print(f"\n💰 Examples of records with empty amount ({empty_amount:,} total):")
            cursor.execute("""
                SELECT id, time, amount, type, name, from_address, to_address, claw_machine, page_number
                FROM transactions 
                WHERE amount = ''
                LIMIT 5
            """)
            examples = cursor.fetchall()
            for ex in examples:
                print(f"  ID: {ex[0]} | Time: '{ex[1]}' | Amount: '{ex[2]}' | Type: '{ex[3]}' | Name: '{ex[4]}'")
        
        # Show examples of records with empty type
        if empty_type > 0:
            print(f"\n🏷️  Examples of records with empty type ({empty_type:,} total):")
            cursor.execute("""
                SELECT id, time, amount, type, name, from_address, to_address, claw_machine, page_number
                FROM transactions 
                WHERE type = ''
                LIMIT 5
            """)
            examples = cursor.fetchall()
            for ex in examples:
                print(f"  ID: {ex[0]} | Time: '{ex[1]}' | Amount: '{ex[2]}' | Type: '{ex[3]}' | Name: '{ex[4]}'")
        
        # Show examples of records with empty name
        if empty_name > 0:
            print(f"\n📝 Examples of records with empty name ({empty_name:,} total):")
            cursor.execute("""
                SELECT id, time, amount, type, name, from_address, to_address, claw_machine, page_number
                FROM transactions 
                WHERE name = ''
                LIMIT 5
            """)
            examples = cursor.fetchall()
            for ex in examples:
                print(f"  ID: {ex[0]} | Time: '{ex[1]}' | Amount: '{ex[2]}' | Type: '{ex[3]}' | Name: '{ex[4]}'")
        
        # Show examples of completely empty records
        print(f"\n🗑️  Examples of completely empty records:")
        cursor.execute("""
            SELECT id, time, amount, type, name, from_address, to_address, claw_machine, page_number
            FROM transactions 
            WHERE time = '' AND amount = '' AND type = '' AND name = ''
            LIMIT 5
        """)
        examples = cursor.fetchall()
        if examples:
            for ex in examples:
                print(f"  ID: {ex[0]} | Time: '{ex[1]}' | Amount: '{ex[2]}' | Type: '{ex[3]}' | Name: '{ex[4]}'")
        else:
            print("  No completely empty records found")
        
        # Show examples of records with multiple empty fields
        print(f"\n⚠️  Examples of records with multiple empty fields:")
        cursor.execute("""
            SELECT id, time, amount, type, name, from_address, to_address, claw_machine, page_number
            FROM transactions 
            WHERE (time = '' AND amount = '') OR (time = '' AND type = '') OR (amount = '' AND type = '')
            LIMIT 5
        """)
        examples = cursor.fetchall()
        if examples:
            for ex in examples:
                print(f"  ID: {ex[0]} | Time: '{ex[1]}' | Amount: '{ex[2]}' | Type: '{ex[3]}' | Name: '{ex[4]}'")
        else:
            print("  No records with multiple empty fields found")
        
        # Summary
        print("\n" + "=" * 35)
        print("📊 Summary:")
        print("=" * 35)
        print(f"Total records: {total_count:,}")
        print(f"Records with empty time: {empty_time:,}")
        print(f"Records with empty amount: {empty_amount:,}")
        print(f"Records with empty type: {empty_type:,}")
        print(f"Records with empty name: {empty_name:,}")
        print(f"Records with empty from_address: {empty_from:,}")
        print(f"Records with empty to_address: {empty_to:,}")
        print(f"Records with empty claw_machine: {empty_claw:,}")
        print(f"Records with empty page_number: {empty_page:,}")
        
        # Calculate records that would be removed
        cursor.execute("""
            SELECT COUNT(*) 
            FROM transactions 
            WHERE time = '' OR amount = '' OR type = '' OR name = ''
        """)
        records_to_remove = cursor.fetchone()[0]
        records_to_keep = total_count - records_to_remove
        
        print(f"\n🧹 Cleanup would remove: {records_to_remove:,} records")
        print(f"✅ Cleanup would keep: {records_to_keep:,} records")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = show_empty_records()
    sys.exit(0 if success else 1)
