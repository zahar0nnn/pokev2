-- Initialize the scraped_data database
USE scraped_data;

-- Create transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME,  -- Primary date field for ordering
    page_number INT,
    batch_number INT,
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
    INDEX idx_date (date),
    INDEX idx_page_number (page_number),
    INDEX idx_batch_number (batch_number),
    INDEX idx_time (time)
);

-- Create scraped_pages table for tracking progress
CREATE TABLE IF NOT EXISTS scraped_pages (
    page_number INT PRIMARY KEY,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create additional indexes for better performance
CREATE INDEX idx_type ON transactions(type);
CREATE INDEX idx_claw_machine ON transactions(claw_machine);
CREATE INDEX idx_from_address ON transactions(from_address);
CREATE INDEX idx_to_address ON transactions(to_address);
CREATE INDEX idx_name ON transactions(name);
CREATE INDEX idx_price ON transactions(price);
CREATE INDEX idx_created_at ON transactions(created_at);
