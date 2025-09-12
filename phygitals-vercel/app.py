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

def get_price_history(item_name, exclude_incomplete=True, filters=None):
    """Get price history for a specific item with optional filtering"""
    data = load_data()
    history = []
    
    # Default empty filters if none provided
    if filters is None:
        filters = {}
    
    for item in data:
        if item.get('name') == item_name and item.get('price') is not None:
            # Apply additional filters to match main table filtering
            if filters:
                # Filter by transaction type
                if 'type' in filters and item.get('type') != filters['type']:
                    continue
                
                # Filter by claw machine type
                if 'claw_machine' in filters and item.get('Claw Machine') != filters['claw_machine']:
                    continue
                
                # Filter by from address
                if 'from_address' in filters and item.get('from') != filters['from_address']:
                    continue
                
                # Filter by to address
                if 'to_address' in filters and item.get('to') != filters['to_address']:
                    continue
                
                # Filter by price range
                if 'min_price' in filters and item.get('price', 0) < float(filters['min_price']):
                    continue
                
                if 'max_price' in filters and item.get('price', 0) > float(filters['max_price']):
                    continue
                
                # Exclude specific addresses
                if 'exclude_from_address' in filters and item.get('from') == filters['exclude_from_address']:
                    continue
                
                if 'exclude_to_address' in filters and item.get('to') == filters['exclude_to_address']:
                    continue
                
                # Filter by modal transaction source (overrides main table claw_machine filter)
                if 'modal_transaction_source' in filters and item.get('Claw Machine') != filters['modal_transaction_source']:
                    continue
                
                # Filter by modal transaction type (overrides main table type filter)
                if 'modal_transaction_type' in filters and item.get('type') != filters['modal_transaction_type']:
                    continue
                
                # Filter by modal from address (overrides main table from_address filter)
                if 'modal_from_address' in filters and item.get('from') != filters['modal_from_address']:
                    continue
            
            # Check if we should exclude incomplete records
            if exclude_incomplete:
                # Skip records with missing essential fields
                if (not item.get('time') or 
                    not item.get('amount') or 
                    not item.get('type') or 
                    not item.get('name')):
                    continue
            
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
                        'claw_machine': item.get('Claw Machine', ''),
                        'is_complete': bool(item.get('time') and item.get('amount') and item.get('type') and item.get('name'))
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
    """API endpoint to get price history for a specific item with filtering options"""
    # Get filter parameters
    exclude_incomplete = request.args.get('exclude_incomplete', 'true').lower() == 'true'
    show_stats = request.args.get('show_stats', 'false').lower() == 'true'
    
    # Get additional filter parameters to match main table filtering
    filters = {
        'type': request.args.get('type', ''),
        'claw_machine': request.args.get('claw_machine', ''),
        'from_address': request.args.get('from', ''),
        'to_address': request.args.get('to', ''),
        'min_price': request.args.get('min_price', ''),
        'max_price': request.args.get('max_price', ''),
        'exclude_from_address': request.args.get('exclude_from_address', ''),
        'exclude_to_address': request.args.get('exclude_to_address', ''),
        'modal_transaction_source': request.args.get('modal_transaction_source', ''),
        'modal_transaction_type': request.args.get('modal_transaction_type', ''),
        'modal_from_address': request.args.get('modal_from_address', '')
    }
    
    # Remove empty filters
    filters = {k: v for k, v in filters.items() if v}
    
    history = get_price_history(item_name, exclude_incomplete, filters)
    
    if show_stats:
        # Calculate statistics
        total_records = len(load_data())
        complete_records = len([item for item in load_data() if item.get('name') == item_name and item.get('time') and item.get('amount') and item.get('type') and item.get('name')])
        incomplete_records = total_records - complete_records
        
        return jsonify({
            'history': history,
            'stats': {
                'total_records': total_records,
                'complete_records': complete_records,
                'incomplete_records': incomplete_records,
                'filtered_records': len(history),
                'excluded_records': complete_records - len(history) if exclude_incomplete else 0
            }
        })
    
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
    app.run(debug=True, host='0.0.0.0', port=5001)
