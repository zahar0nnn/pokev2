#!/usr/bin/env python3
"""
Simple Flask test to isolate the issue
"""

from flask import Flask, jsonify
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

@app.route('/')
def index():
    """Simple test route"""
    return """
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1>✅ Flask is working!</h1>
        <p>If you can see this, Flask is running correctly.</p>
        <p><a href="/test">Test API</a></p>
        <p><a href="/debug">Debug Info</a></p>
    </body>
    </html>
    """

@app.route('/test')
def test():
    """Simple test API"""
    return jsonify({
        "status": "success",
        "message": "API is working",
        "timestamp": "2025-01-08"
    })

@app.route('/debug')
def debug():
    """Debug route"""
    try:
        # Try to import database config
        from database_config import DatabaseConfig
        db = DatabaseConfig()
        
        # Try to get connection
        connection = db.get_connection()
        if connection:
            return jsonify({
                "status": "success",
                "database": "connected",
                "message": "Database connection working"
            })
        else:
            return jsonify({
                "status": "error",
                "database": "not_connected",
                "message": "Database connection failed"
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error: {str(e)}",
            "type": type(e).__name__
        })

if __name__ == '__main__':
    print("🧪 Starting Simple Flask Test")
    print("🌐 Visit: http://127.0.0.1:5001")
    print("💡 Press Ctrl+C to stop")
    app.run(debug=True, host='127.0.0.1', port=5001)
