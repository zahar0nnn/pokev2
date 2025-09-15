#!/usr/bin/env python3
"""
Optimized Flask web application for Phygitals data
"""

from flask import Flask, render_template, jsonify, request
from database import Database
from flask_cors import CORS
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize database
try:
    db = Database()
    db.setup_database()
    logger.info("✅ Database initialized successfully")
except Exception as e:
    logger.error(f"❌ Database initialization failed: {e}")
    db = None

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """Get paginated transactions"""
    if not db:
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(max(1, int(request.args.get('per_page', 50))), 200)  # Max 200 per page
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get transactions
        transactions = db.get_transactions(limit=per_page, offset=offset)
        
        # Get total count
        stats = db.get_stats()
        total_count = stats.get('total_records', 0)
        
        return jsonify({
            'data': transactions,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'pages': (total_count + per_page - 1) // per_page
        })
        
    except (ValueError, TypeError) as e:
        logger.error(f"❌ Invalid parameters: {e}")
        return jsonify({'error': 'Invalid parameters'}), 400
    except Exception as e:
        logger.error(f"❌ Error getting data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search')
def search_data():
    """Search transactions with filters"""
    if not db:
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        # Get filters from query parameters
        filters = {
            'min_price': request.args.get('min_price'),
            'max_price': request.args.get('max_price'),
            'type': request.args.get('type'),
            'claw_machine': request.args.get('claw_machine'),
            'name': request.args.get('name')
        }
        
        # Remove empty filters
        filters = {k: v for k, v in filters.items() if v}
        
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(max(1, int(request.args.get('per_page', 50))), 200)
        offset = (page - 1) * per_page
        
        # Search transactions
        transactions = db.search_transactions(filters, limit=per_page, offset=offset)
        
        # Get total count for search (limited to avoid performance issues)
        total_count = len(db.search_transactions(filters, limit=10000, offset=0))
        
        return jsonify({
            'data': transactions,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'pages': (total_count + per_page - 1) // per_page
        })
        
    except (ValueError, TypeError) as e:
        logger.error(f"❌ Invalid parameters: {e}")
        return jsonify({'error': 'Invalid parameters'}), 400
    except Exception as e:
        logger.error(f"❌ Error searching data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/filters')
def get_filters():
    """Get available filter options"""
    if not db:
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        filters = {
            'types': db.get_unique_values('transaction_type'),
            'claw_machines': db.get_unique_values('claw_machine'),
            'names': db.get_unique_values('item_name')[:100]  # Limit names to 100
        }
        
        return jsonify(filters)
        
    except Exception as e:
        logger.error(f"❌ Error getting filters: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/price_history/<item_name>')
def get_price_history(item_name):
    """Get price history for a specific item"""
    if not db:
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        filters = {'name': item_name}
        transactions = db.search_transactions(filters, limit=1000, offset=0)
        
        # Sort by time and extract price data
        price_data = []
        for transaction in transactions:
            if transaction.get('price') and transaction.get('time'):
                try:
                    price_data.append({
                        'time': transaction['time'],
                        'price': float(transaction['price'])
                    })
                except (ValueError, TypeError) as e:
                    logger.warning(f"⚠️  Invalid price data: {e}")
                    continue
        
        # Sort by time (handle both string and datetime objects)
        try:
            price_data.sort(key=lambda x: x['time'])
        except TypeError:
            # If time is not comparable, convert to datetime first
            price_data.sort(key=lambda x: datetime.fromisoformat(x['time'].replace('Z', '+00:00')) if isinstance(x['time'], str) else x['time'])
        
        return jsonify(price_data)
        
    except Exception as e:
        logger.error(f"❌ Error getting price history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get scraping statistics"""
    if not db:
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        stats = db.get_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/debug')
def debug():
    """Debug endpoint"""
    try:
        if not db:
            return jsonify({
                'status': 'error',
                'database': 'not_initialized',
                'error': 'Database not initialized',
                'timestamp': str(datetime.now())
            }), 500
        
        stats = db.get_stats()
        return jsonify({
            'status': 'ok',
            'database': 'connected',
            'stats': stats,
            'timestamp': str(datetime.now())
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': str(datetime.now())
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("🌐 Starting Phygitals Web App")
    logger.info("=" * 40)
    
    # Test database connection
    try:
        stats = db.get_stats()
        logger.info(f"✅ Database connected - {stats.get('total_records', 0)} records")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
    
    logger.info("🚀 Starting Flask server...")
    app.run(host='0.0.0.0', port=5001, debug=False)
