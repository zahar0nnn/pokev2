from flask import Flask, render_template, jsonify, request
import json
import csv
from datetime import datetime
import os
from database_config import DatabaseConfig

app = Flask(__name__)

# Initialize database connection
db = DatabaseConfig()

def load_data():
    """Load scraped data from MySQL database"""
    try:
        print("Loading data from MySQL database...")
        data = db.get_all_transactions()
        print(f"Loaded {len(data)} items from database")
        return data
    except Exception as e:
        print(f"Error loading data from database: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_unique_values(field):
    """Get unique values for a specific field"""
    data = load_data()
    unique_values = set()
    for item in data:
        if field in item and item[field]:
            unique_values.add(item[field])
    return sorted(list(unique_values))

def get_price_history(item_name):
    """Get price history for a specific item"""
    data = load_data()
    history = []
    
    for item in data:
        if item.get('name') == item_name and item.get('price'):
            try:
                # Parse time to get date
                time_str = item.get('time', '')
                if time_str:
                    # Convert ISO format to datetime
                    dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    history.append({
                        'date': dt.strftime('%Y-%m-%d'),
                        'datetime': dt.isoformat(),
                        'price': item['price'],
                        'amount': item.get('amount', 0),
                        'type': item.get('type', ''),
                        'from': item.get('from', ''),
                        'to': item.get('to', ''),
                        'claw_machine': item.get('Claw Machine', '')
                    })
            except Exception as e:
                print(f"Error parsing time for item {item_name}: {e}")
                continue
    
    # Sort by date
    history.sort(key=lambda x: x['datetime'])
    return history

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/debug')
def debug():
    """Debug endpoint to check file paths and data loading"""
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, 'scraped_data.json')
    file_exists = os.path.exists(file_path)
    
    # Try to load data
    data = load_data()
    
    debug_info = {
        'current_directory': current_dir,
        'file_path': file_path,
        'file_exists': file_exists,
        'data_loaded': len(data),
        'files_in_dir': os.listdir(current_dir) if os.path.exists(current_dir) else []
    }
    
    return jsonify(debug_info)

@app.route('/api/data')
def api_data():
    """API endpoint to get all data"""
    data = load_data()
    return jsonify(data)

@app.route('/api/filters')
def api_filters():
    """API endpoint to get filter options from MySQL"""
    filters = {
        'types': db.get_unique_values('type'),
        'claw_machines': db.get_unique_values('claw_machine'),
        'from_addresses': db.get_unique_values('from_address'),
        'to_addresses': db.get_unique_values('to_address'),
        'names': db.get_unique_values('name')
    }
    return jsonify(filters)

@app.route('/api/price_history/<item_name>')
def api_price_history(item_name):
    """API endpoint to get price history for a specific item"""
    history = get_price_history(item_name)
    return jsonify(history)

@app.route('/api/search')
def api_search():
    """API endpoint for filtered search using MySQL"""
    # Get filter parameters
    filters = {
        'type': request.args.get('type', ''),
        'claw_machine': request.args.get('claw_machine', ''),
        'from_address': request.args.get('from', ''),
        'to_address': request.args.get('to', ''),
        'name': request.args.get('name', ''),
        'min_price': request.args.get('min_price', ''),
        'max_price': request.args.get('max_price', '')
    }
    
    # Remove empty filters
    filters = {k: v for k, v in filters.items() if v}
    
    print(f"Search parameters: {filters}")
    
    # Use database search
    filtered_data = db.search_transactions(filters)
    print(f"Database search results: {len(filtered_data)} items")
    
    return jsonify(filtered_data)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)
