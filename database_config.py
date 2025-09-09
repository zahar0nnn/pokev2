import mysql.connector
from mysql.connector import Error
import os

class DatabaseConfig:
    def __init__(self):
        self.host = os.getenv('MYSQL_HOST', 'localhost')
        self.port = os.getenv('MYSQL_PORT', '3306')
        self.user = os.getenv('MYSQL_USER', 'root')
        self.password = os.getenv('MYSQL_PASSWORD', 'my-secret-pw')
        self.database = os.getenv('MYSQL_DATABASE', 'scraped_data')
    
    def get_connection(self):
        """Get MySQL database connection"""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def create_database_and_tables(self):
        """Create database and tables if they don't exist"""
        connection = None
        cursor = None
        try:
            # First connect without database to create it
            connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            cursor.execute(f"USE {self.database}")
            
            # Create transactions table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date VARCHAR(255),  -- Primary date field for ordering
                page_number INT,    -- Keep for reference but not primary
                batch_number INT,   -- Date-based batch number
                time VARCHAR(255),  -- Keep for compatibility
                amount VARCHAR(255),
                type VARCHAR(255),
                claw_machine VARCHAR(50),
                from_address VARCHAR(255),
                to_address VARCHAR(255),
                name TEXT,
                price DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_transaction (time, amount, type),
                INDEX idx_date (date),  -- Index for date-based queries
                INDEX idx_time (time)   -- Index for time-based queries
            )
            """
            cursor.execute(create_table_query)
            
            # Check if date column exists, if not add it
            cursor.execute("DESCRIBE transactions")
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]
            
            if 'date' not in column_names:
                print("📝 Adding date column to existing transactions table...")
                cursor.execute("ALTER TABLE transactions ADD COLUMN date VARCHAR(255)")
                print("✅ Date column added to existing table")
            
            # Check if indexes exist, if not add them
            cursor.execute("SHOW INDEX FROM transactions")
            indexes = cursor.fetchall()
            index_names = [idx[2] for idx in indexes]
            
            if 'idx_date' not in index_names:
                print("📝 Adding date index...")
                cursor.execute("CREATE INDEX idx_date ON transactions (date)")
                print("✅ Date index added")
            
            if 'idx_time' not in index_names:
                print("📝 Adding time index...")
                cursor.execute("CREATE INDEX idx_time ON transactions (time)")
                print("✅ Time index added")
            
            # Create scraped_pages table for tracking progress
            create_pages_table = """
            CREATE TABLE IF NOT EXISTS scraped_pages (
                page_number INT PRIMARY KEY,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_pages_table)
            
            connection.commit()
            print(f"Database '{self.database}' and tables created successfully")
            
        except Error as e:
            print(f"Error creating database: {e}")
            # Check if it's a connection error
            if "Can't connect to MySQL server" in str(e):
                print("❌ MySQL server is not running or not accessible.")
                print("💡 Please start MySQL server or check your connection settings.")
                print(f"   Host: {self.host}:{self.port}")
                print(f"   User: {self.user}")
                print(f"   Database: {self.database}")
            raise e
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def insert_transaction(self, transaction_data):
        """Insert a single transaction into the database"""
        connection = self.get_connection()
        if not connection:
            return False
            
        try:
            cursor = connection.cursor()
            
            # Convert amount to price
            price = 0
            amount_value = transaction_data.get('amount')
            if amount_value and str(amount_value).strip():
                try:
                    amount = int(str(amount_value).strip())
                    if amount > 0:  # Only calculate price for positive amounts
                        price = round(amount / 1000000, 2)
                except (ValueError, TypeError):
                    price = 0
            
            insert_query = """
            INSERT INTO transactions 
            (date, page_number, batch_number, time, amount, type, claw_machine, from_address, to_address, name, price)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            date = VALUES(date),
            page_number = VALUES(page_number),
            batch_number = VALUES(batch_number),
            claw_machine = VALUES(claw_machine),
            from_address = VALUES(from_address),
            to_address = VALUES(to_address),
            name = VALUES(name),
            price = VALUES(price)
            """
            
            values = (
                transaction_data.get('date', transaction_data.get('time', '')),  # Use date field, fallback to time
                transaction_data.get('page', 0),
                transaction_data.get('batch', 0),
                transaction_data.get('time', ''),
                transaction_data.get('amount', ''),
                transaction_data.get('type', ''),
                transaction_data.get('Claw Machine', ''),
                transaction_data.get('from', ''),
                transaction_data.get('to', ''),
                transaction_data.get('name', ''),
                price
            )
            
            cursor.execute(insert_query, values)
            connection.commit()
            return True
            
        except Error as e:
            print(f"Error inserting transaction: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def insert_transactions_batch(self, transactions):
        """Insert multiple transactions in batch"""
        connection = self.get_connection()
        if not connection:
            return False
            
        try:
            cursor = connection.cursor()
            
            insert_query = """
            INSERT INTO transactions 
            (date, page_number, batch_number, time, amount, type, claw_machine, from_address, to_address, name, price)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            date = VALUES(date),
            page_number = VALUES(page_number),
            batch_number = VALUES(batch_number),
            claw_machine = VALUES(claw_machine),
            from_address = VALUES(from_address),
            to_address = VALUES(to_address),
            name = VALUES(name),
            price = VALUES(price)
            """
            
            values_list = []
            for transaction_data in transactions:
                # Convert amount to price
                price = 0
                amount_value = transaction_data.get('amount')
                if amount_value and str(amount_value).strip():
                    try:
                        amount = int(str(amount_value).strip())
                        if amount > 0:  # Only calculate price for positive amounts
                            price = round(amount / 1000000, 2)
                    except (ValueError, TypeError):
                        price = 0
                
                values = (
                    transaction_data.get('date', transaction_data.get('time', '')),  # Use date field, fallback to time
                    transaction_data.get('page', 0),
                    transaction_data.get('batch', 0),
                    transaction_data.get('time', ''),
                    transaction_data.get('amount', ''),
                    transaction_data.get('type', ''),
                    transaction_data.get('Claw Machine', ''),
                    transaction_data.get('from', ''),
                    transaction_data.get('to', ''),
                    transaction_data.get('name', ''),
                    price
                )
                values_list.append(values)
            
            cursor.executemany(insert_query, values_list)
            connection.commit()
            print(f"Inserted {len(transactions)} transactions into database")
            return True
            
        except Error as e:
            print(f"Error inserting transactions batch: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def mark_page_scraped(self, page_number):
        """Mark a page as scraped"""
        connection = self.get_connection()
        if not connection:
            return False
            
        try:
            cursor = connection.cursor()
            insert_query = "INSERT IGNORE INTO scraped_pages (page_number) VALUES (%s)"
            cursor.execute(insert_query, (page_number,))
            connection.commit()
            return True
        except Error as e:
            print(f"Error marking page as scraped: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def get_scraped_pages(self):
        """Get list of already scraped pages"""
        connection = self.get_connection()
        if not connection:
            return set()
            
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT page_number FROM scraped_pages")
            pages = {row[0] for row in cursor.fetchall()}
            return pages
        except Error as e:
            print(f"Error getting scraped pages: {e}")
            return set()
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def get_all_transactions(self):
        """Get all transactions from database"""
        connection = self.get_connection()
        if not connection:
            return []
            
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT date, page_number as page, batch_number as batch, time, amount, type, 
                       claw_machine as 'Claw Machine', from_address as 'from', 
                       to_address as 'to', name, price
                FROM transactions 
                ORDER BY date DESC, time DESC
            """)
            transactions = cursor.fetchall()
            return transactions
        except Error as e:
            print(f"Error getting transactions: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def search_transactions(self, filters):
        """Search transactions with filters"""
        connection = self.get_connection()
        if not connection:
            return []
            
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Build WHERE clause based on filters
            where_conditions = []
            params = []
            
            if filters.get('min_price'):
                where_conditions.append("price >= %s")
                params.append(float(filters['min_price']))
            
            if filters.get('max_price'):
                where_conditions.append("price <= %s")
                params.append(float(filters['max_price']))
            
            if filters.get('type'):
                where_conditions.append("type = %s")
                params.append(filters['type'])
            
            if filters.get('claw_machine'):
                if filters['claw_machine'] == 'Claw Machine':
                    where_conditions.append("claw_machine = 'Claw Machine'")
                elif filters['claw_machine'] == 'Human':
                    where_conditions.append("claw_machine = 'human'")
            
            if filters.get('from_address'):
                where_conditions.append("from_address = %s")
                params.append(filters['from_address'])
            
            if filters.get('to_address'):
                where_conditions.append("to_address = %s")
                params.append(filters['to_address'])
            
            if filters.get('name'):
                where_conditions.append("name LIKE %s")
                params.append(f"%{filters['name']}%")
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            query = f"""
                SELECT date, page_number as page, batch_number as batch, time, amount, type, 
                       claw_machine as 'Claw Machine', from_address as 'from', 
                       to_address as 'to', name, price
                FROM transactions 
                WHERE {where_clause}
                ORDER BY date DESC, time DESC
            """
            
            cursor.execute(query, params)
            transactions = cursor.fetchall()
            return transactions
            
        except Error as e:
            print(f"Error searching transactions: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def get_unique_values(self, column):
        """Get unique values for a specific column"""
        connection = self.get_connection()
        if not connection:
            return []
            
        try:
            cursor = connection.cursor()
            cursor.execute(f"SELECT DISTINCT {column} FROM transactions WHERE {column} IS NOT NULL AND {column} != ''")
            values = [row[0] for row in cursor.fetchall()]
            return values
        except Error as e:
            print(f"Error getting unique values for {column}: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
