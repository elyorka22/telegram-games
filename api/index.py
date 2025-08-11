from flask import Flask, jsonify, request
import os

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def api_root():
    """API root endpoint"""
    return jsonify({
        'message': 'Telegram Games API is running on Vercel!',
        'status': 'ok',
        'platform': 'vercel',
        'endpoints': [
            '/api/status',
            '/api/health',
            '/api/test'
        ]
    })

@app.route('/api/status', methods=['GET'])
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'running',
        'environment': os.getenv('VERCEL_ENV', 'development'),
        'region': os.getenv('VERCEL_REGION', 'unknown'),
        'platform': 'vercel',
        'version': '1.0.0'
    })

@app.route('/api/health', methods=['GET'])
def api_health():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'message': 'API is running on Vercel',
        'platform': 'vercel'
    }), 200

@app.route('/api/test', methods=['GET'])
def api_test():
    """API test endpoint"""
    return jsonify({
        'message': 'API test endpoint working on Vercel!',
        'status': 'ok',
        'platform': 'vercel'
    }), 200

# Export the Flask app for Vercel
app.debug = False 