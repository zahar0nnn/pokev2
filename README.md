# Phygitals Scraper with MySQL and Docker

This project scrapes transaction data from the Phygitals API and stores it in a MySQL database, with a web interface for viewing and filtering the data.

## Features

- **Web Scraping**: Scrapes transaction data from Phygitals API with multiprocessing support
- **MySQL Database**: Stores data in a structured MySQL database with proper indexing
- **Web Interface**: Flask-based web application with filtering and price history charts
- **Server-Side Pagination**: Fast, scalable pagination with 25-200 items per page
- **Server-Side Sorting**: Efficient sorting in MySQL database
- **Docker Support**: Complete Docker Compose setup for easy deployment
- **Resume Functionality**: Can resume scraping from where it left off
- **Data Deduplication**: Automatically removes duplicate transactions
- **Performance Optimized**: Low memory usage, fast loading even with millions of records

## Quick Start with Docker

### Windows PowerShell:
1. **Start the services**:
   ```powershell
   .\update_docker.ps1
   ```

2. **Access the web application**:
   - Open http://localhost:5001 in your browser

3. **Run the scraper** (optional):
   ```powershell
   docker-compose run scraper python scraper.py
   ```

### Linux/Mac:
1. **Start the services**:
   ```bash
   docker-compose up -d
   ```

2. **Access the web application**:
   - Open http://localhost:5001 in your browser

3. **Run the scraper** (optional):
   ```bash
   docker-compose run scraper python scraper.py
   ```

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

## Troubleshooting

1. **MySQL connection issues**:
   - Check if MySQL is running
   - Verify connection credentials
   - Run `python test_mysql.py` to test connection

2. **Web app not loading data**:
   - Check if data exists in the database
   - Verify Flask app is connecting to the correct database
   - Check console logs for errors

3. **Scraper issues**:
   - Check internet connection
   - Verify API endpoint is accessible
   - Check for rate limiting

## File Structure

```
├── app.py                 # Flask web application
├── scraper.py            # Main scraper script
├── database_config.py    # MySQL database configuration
├── docker-compose.yaml   # Docker Compose configuration
├── Dockerfile.scraper    # Scraper Docker image
├── Dockerfile.webapp     # Web app Docker image
├── init.sql             # Database initialization
├── requirements.txt     # Python dependencies
├── test_mysql.py       # MySQL connection test
└── templates/
    └── index.html      # Web interface template
```

## License

This project is for educational and research purposes.
