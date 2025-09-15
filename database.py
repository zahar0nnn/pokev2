#!/usr/bin/env python3
"""
Optimized MySQL database layer for Phygitals scraper
"""

import mysql.connector
from mysql.connector import Error, pooling
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    """Optimized database class with connection pooling and better error handling"""
    
    def __init__(self):
        """Initialize database with environment variables"""
        self.config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', '3306')),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', 'my-secret-pw'),
            'database': os.getenv('MYSQL_DATABASE', 'phygitals_data'),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': True,
            'pool_name': 'phygitals_pool',
            'pool_size': 10,
            'pool_reset_session': True
        }
        
        self.pool = None
        self._database_created = False
        # Don't create pool immediately - wait for setup_database to be called
    
    def _create_pool(self):
        """Create connection pool"""
        try:
            # Don't try to create pool if database doesn't exist yet
            if not hasattr(self, '_database_created'):
                return
            
            self.pool = pooling.MySQLConnectionPool(**self.config)
            logger.info("✅ Database connection pool created")
        except Error as e:
            logger.error(f"❌ Failed to create connection pool: {e}")
            self.pool = None
    
    def get_connection(self):
        """Get connection from pool"""
        if not self.pool:
            # Try to create pool if it doesn't exist
            self._create_pool()
            if not self.pool:
                return None
        try:
            return self.pool.get_connection()
        except Error as e:
            logger.error(f"❌ Failed to get connection: {e}")
            return None
    
    def setup_database(self):
        """Create database and tables"""
        connection = None
        try:
            # Connect without database first
            connection = mysql.connector.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                charset=self.config['charset'],
                collation=self.config['collation']
            )
            
            cursor = connection.cursor()
            
            # Create database (using parameterized queries for safety)
            database_name = self.config['database']
            charset = self.config['charset']
            collation = self.config['collation']
            
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}` "
                          f"CHARACTER SET {charset} "
                          f"COLLATE {collation}")
            cursor.execute(f"USE `{database_name}`")
            
            # Create transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    transaction_id VARCHAR(255) UNIQUE NOT NULL,
                    page_number INT NOT NULL,
                    batch_number INT NOT NULL,
                    transaction_time DATETIME NOT NULL,
                    amount BIGINT NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    transaction_type VARCHAR(50) NOT NULL,
                    claw_machine VARCHAR(20) NOT NULL,
                    from_address VARCHAR(255) NOT NULL,
                    to_address VARCHAR(255) NOT NULL,
                    item_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    
                    INDEX idx_transaction_time (transaction_time),
                    INDEX idx_page_number (page_number),
                    INDEX idx_batch_number (batch_number),
                    INDEX idx_price (price),
                    INDEX idx_transaction_type (transaction_type),
                    INDEX idx_claw_machine (claw_machine),
                    INDEX idx_item_name (item_name(100)),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Create scraped_pages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraped_pages (
                    page_number INT PRIMARY KEY,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    records_count INT DEFAULT 0,
                    INDEX idx_scraped_at (scraped_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Create stats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraping_stats (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    total_pages INT DEFAULT 0,
                    total_records INT DEFAULT 0,
                    last_scraped_page INT DEFAULT 0,
                    last_scraped_time TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Insert initial stats
            cursor.execute("""
                INSERT IGNORE INTO scraping_stats (id, total_pages, total_records, last_scraped_page)
                VALUES (1, 0, 0, 0)
            """)
            
            connection.commit()
            logger.info("✅ Database and tables created successfully")
            
            # Mark database as created and recreate pool
            self._database_created = True
            self._create_pool()
            
        except Error as e:
            logger.error(f"❌ Database setup failed: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                if 'cursor' in locals():
                    cursor.close()
                connection.close()
    
    def insert_transactions_batch(self, transactions: List[Dict[str, Any]]) -> bool:
        """Insert multiple transactions efficiently"""
        if not transactions:
            return True
        
        connection = self.get_connection()
        if not connection:
            return False
        
        cursor = None
        try:
            cursor = connection.cursor()
            
            # Prepare batch data
            batch_data = []
            for tx in transactions:
                try:
                    transaction_id = f"{tx['page']}_{tx['time']}_{tx['amount']}"
                    transaction_time = self._parse_time(tx.get('time', ''))
                    amount = int(tx.get('amount', 0))
                    price = round(amount / 1000000, 2) if amount > 0 else 0
                    
                    batch_data.append((
                        transaction_id,
                        tx.get('page', 0),
                        tx.get('batch', 0),
                        transaction_time,
                        amount,
                        price,
                        tx.get('type', ''),
                        tx.get('claw_machine', ''),
                        tx.get('from', ''),
                        tx.get('to', ''),
                        tx.get('name', '')
                    ))
                except (ValueError, TypeError, KeyError) as e:
                    logger.warning(f"⚠️  Skipping invalid transaction: {e}")
                    continue
            
            if not batch_data:
                logger.warning("⚠️  No valid transactions to insert")
                return True
            
            # Insert with ON DUPLICATE KEY UPDATE
            cursor.executemany("""
                INSERT INTO transactions (
                    transaction_id, page_number, batch_number, transaction_time, amount, price,
                    transaction_type, claw_machine, from_address, to_address, item_name
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    transaction_time = VALUES(transaction_time),
                    amount = VALUES(amount),
                    price = VALUES(price),
                    transaction_type = VALUES(transaction_type),
                    claw_machine = VALUES(claw_machine),
                    from_address = VALUES(from_address),
                    to_address = VALUES(to_address),
                    item_name = VALUES(item_name),
                    updated_at = CURRENT_TIMESTAMP
            """, batch_data)
            
            logger.info(f"✅ Inserted {len(batch_data)} transactions")
            return True
            
        except Error as e:
            logger.error(f"❌ Error inserting batch: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def mark_page_scraped(self, page_number: int, records_count: int = 0) -> bool:
        """Mark a page as scraped and update stats"""
        connection = self.get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            
            # Mark page as scraped
            cursor.execute("""
                INSERT INTO scraped_pages (page_number, records_count)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE
                    records_count = VALUES(records_count),
                    scraped_at = CURRENT_TIMESTAMP
            """, (page_number, records_count))
            
            # Update stats
            cursor.execute("""
                UPDATE scraping_stats SET
                    total_pages = (SELECT COUNT(*) FROM scraped_pages),
                    total_records = (SELECT COUNT(*) FROM transactions),
                    last_scraped_page = %s,
                    last_scraped_time = CURRENT_TIMESTAMP
                WHERE id = 1
            """, (page_number,))
            
            return True
            
        except Error as e:
            logger.error(f"❌ Error marking page scraped: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def get_scraped_pages(self) -> set:
        """Get list of scraped pages"""
        connection = self.get_connection()
        if not connection:
            return set()
        
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT page_number FROM scraped_pages")
            return {row[0] for row in cursor.fetchall()}
        except Error as e:
            logger.error(f"❌ Error getting scraped pages: {e}")
            return set()
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        connection = self.get_connection()
        if not connection:
            return {}
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM scraping_stats WHERE id = 1")
            return cursor.fetchone() or {}
        except Error as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {}
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def get_transactions(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """Get transactions with pagination"""
        connection = self.get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    transaction_id,
                    page_number as page,
                    batch_number as batch,
                    transaction_time as time,
                    amount,
                    price,
                    transaction_type as type,
                    claw_machine as 'Claw Machine',
                    from_address as 'from',
                    to_address as 'to',
                    item_name as name,
                    created_at
                FROM transactions 
                ORDER BY transaction_time DESC, id DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            
            return cursor.fetchall()
        except Error as e:
            logger.error(f"❌ Error getting transactions: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def search_transactions(self, filters: Dict[str, Any], limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """Search transactions with filters"""
        connection = self.get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Build WHERE clause
            where_conditions = []
            params = []
            
            if filters.get('min_price'):
                where_conditions.append("price >= %s")
                params.append(float(filters['min_price']))
            
            if filters.get('max_price'):
                where_conditions.append("price <= %s")
                params.append(float(filters['max_price']))
            
            if filters.get('type'):
                where_conditions.append("transaction_type = %s")
                params.append(filters['type'])
            
            if filters.get('claw_machine'):
                where_conditions.append("claw_machine = %s")
                params.append(filters['claw_machine'])
            
            if filters.get('name'):
                where_conditions.append("item_name LIKE %s")
                params.append(f"%{filters['name']}%")
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            query = f"""
                SELECT 
                    transaction_id,
                    page_number as page,
                    batch_number as batch,
                    transaction_time as time,
                    amount,
                    price,
                    transaction_type as type,
                    claw_machine as 'Claw Machine',
                    from_address as 'from',
                    to_address as 'to',
                    item_name as name,
                    created_at
                FROM transactions 
                WHERE {where_clause}
                ORDER BY transaction_time DESC, id DESC
                LIMIT %s OFFSET %s
            """
            
            params.extend([limit, offset])
            cursor.execute(query, params)
            return cursor.fetchall()
            
        except Error as e:
            logger.error(f"❌ Error searching transactions: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def get_unique_values(self, column: str) -> List[str]:
        """Get unique values for a column"""
        connection = self.get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor()
            cursor.execute(f"SELECT DISTINCT {column} FROM transactions WHERE {column} IS NOT NULL AND {column} != '' ORDER BY {column}")
            return [row[0] for row in cursor.fetchall()]
        except Error as e:
            logger.error(f"❌ Error getting unique values: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def _parse_time(self, time_str: str) -> Optional[datetime]:
        """Parse time string to datetime object"""
        if not time_str:
            return None
        
        try:
            # Try different time formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S.%f'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(time_str, fmt)
                except ValueError:
                    continue
            
            # If no format works, return current time
            logger.warning(f"⚠️  Could not parse time '{time_str}', using current time")
            return datetime.now()
            
        except Exception as e:
            logger.error(f"⚠️  Error parsing time '{time_str}': {e}")
            return datetime.now()
    
    def close(self):
        """Close all connections"""
        if self.pool:
            self.pool.close()
            logger.info("✅ Database connections closed")
