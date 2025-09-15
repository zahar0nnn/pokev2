# Phygitals Scraper - Optimized & Reliable

A high-performance scraper for Phygitals marketplace data with MySQL storage and web interface.

## Features

- **Optimized Scraping**: High-performance scraper with retry logic and error recovery
- **Advanced Database**: MySQL with connection pooling, proper indexing, and statistics
- **Modern Web Interface**: Flask-based web application with filtering, charts, and pagination
- **Docker Support**: Complete Docker Compose setup for easy deployment
- **Progress Tracking**: Real-time progress monitoring with JSON and database stats
- **Robust Error Handling**: Graceful error recovery and logging
- **Easy Setup**: Simple installation and startup process

## Quick Start

### Option 1: Local Setup (Recommended) ⭐
1. **Install Python 3.9+** if not already installed
2. **Run the optimized setup**:
   ```powershell
   # Windows PowerShell
   .\start.ps1
   ```
   ```bash
   # Linux/Mac
   python3 scraper.py
   ```
3. **Start the web app** (in another terminal):
   ```bash
   python3 app.py
   ```
4. **Access the web application**:
   - Open http://localhost:5001 in your browser

### Option 2: Docker Setup
1. **Start the services**:
   ```bash
   docker-compose up -d
   ```

2. **Run the scraper**:
   ```bash
   docker-compose run scraper
   ```

3. **Access the web application**:
   - Open http://localhost:5001 in your browser

## Local Development (without Docker)

### Windows PowerShell:
```powershell
.\start_local.ps1
```

### Linux/Mac:
```bash
pip install -r requirements.txt
python app.py
```

## Pagination Features

The web interface now includes server-side pagination for optimal performance:

- **Configurable Page Size**: Choose between 25, 50, 100, or 200 items per page
- **Server-Side Sorting**: Sort by date, name, price, or transaction count
- **Fast Navigation**: First/Previous/Next/Last buttons with page numbers
- **Memory Efficient**: Only loads current page data, not all records
- **Scalable**: Works efficiently with millions of records

### API Endpoints

- `GET /api/data?page=1&per_page=50&sort_by=date-desc` - Get paginated data
- `GET /api/filters` - Get filter options
- `GET /api/price_history/<item_name>` - Get price history for specific item

## Manual Setup

### Prerequisites

- Python 3.9+
- MySQL 8.0+
- Docker and Docker Compose (optional)

### Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up MySQL database**:
   - Create a MySQL database named `scraped_data`
   - Update connection details in `database_config.py` if needed

3. **Initialize the database**:
   ```bash
   python test_mysql.py
   ```

4. **Run the scraper**:
   ```bash
   python scraper.py
   ```

5. **Start the web application**:
   ```bash
   python app.py
   ```

## Configuration

### Database Configuration

The database connection can be configured using environment variables:

- `MYSQL_HOST`: Database host (default: localhost)
- `MYSQL_PORT`: Database port (default: 3306)
- `MYSQL_USER`: Database user (default: root)
- `MYSQL_PASSWORD`: Database password (default: my-secret-pw)
- `MYSQL_DATABASE`: Database name (default: scraped_data)

### Scraper Configuration

- **Pages to scrape**: Modify the `num_pages` parameter in `scraper.py`
- **Multiprocessing**: Adjust `num_processes` for your CPU
- **Batch size**: Modify `batch_size` for memory management

## API Endpoints

- `GET /`: Main web interface
- `GET /api/data`: Get all transactions
- `GET /api/search`: Search transactions with filters
- `GET /api/filters`: Get available filter options
- `GET /api/price_history/<item_name>`: Get price history for an item

## Database Schema

### transactions table
- `id`: Primary key
- `page_number`: API page number
- `batch_number`: Batch number (every 100 pages)
- `time`: Transaction timestamp
- `amount`: Transaction amount (raw)
- `type`: Transaction type (CLAW, etc.)
- `claw_machine`: "Claw Machine" or "human"
- `from_address`: Sender address
- `to_address`: Receiver address
- `name`: Item name
- `price`: Calculated price (amount / 1,000,000)
- `created_at`: Record creation timestamp

### scraped_pages table
- `page_number`: Page number (primary key)
- `scraped_at`: When the page was scraped

## Docker Services

- **database**: MySQL 8.0 with persistent storage
- **scraper**: Python scraper application
- **webapp**: Flask web application

## Monitoring

### Check Scraper Status
```bash
# Optimized version
python monitor.py
```

### Check Database
```bash
# Connect to MySQL
mysql -h localhost -u root -p

# Check records
USE phygitals_data;
SELECT COUNT(*) FROM transactions;
SELECT MAX(transaction_time) FROM transactions;
```

### Check Web App
```bash
# Test web app
curl http://localhost:5001/debug

# Check logs
docker logs phygitals-webapp
```

## Troubleshooting

1. **Database connection issues**:
   - Check if MySQL is running
   - Verify connection credentials in environment variables
   - Run `python monitor.py` to test connection

2. **Web app not loading data**:
   - Check if data exists in the database
   - Verify Flask app is connecting to the correct database
   - Check console logs for errors

3. **Scraper issues**:
   - Check internet connection
   - Verify API endpoint is accessible
   - Check for rate limiting
   - Run `python monitor.py` to see status

## File Structure

```
├── app.py                 # Optimized Flask web application
├── scraper.py            # Optimized scraper script
├── database.py           # Optimized MySQL database layer
├── monitor.py            # Monitoring and health check script
├── start.ps1             # Windows startup script
├── docker-compose.yaml   # Docker Compose configuration
├── Dockerfile.scraper    # Scraper Docker image
├── Dockerfile.webapp     # Web app Docker image
├── requirements.txt      # Python dependencies
└── templates/
    └── index.html        # Web interface template
```

## License

This project is for educational and research purposes.
