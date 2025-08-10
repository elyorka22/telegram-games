from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Главная страница"""
    return jsonify({
        'message': 'Telegram Games App is running!',
        'status': 'ok',
        'port': os.getenv('PORT', '5000')
    })

@app.route('/health')
def health_check():
    """Health check endpoint для Railway"""
    return jsonify({
        'status': 'healthy',
        'message': 'Application is running',
        'port': os.getenv('PORT', '5000')
    }), 200

@app.route('/test')
def test():
    """Тестовый endpoint"""
    return jsonify({
        'message': 'Test endpoint working!',
        'status': 'ok',
        'port': os.getenv('PORT', '5000')
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = '0.0.0.0'
    
    print(f"Starting app on {host}:{port}")
    print(f"PORT environment variable: {os.getenv('PORT')}")
    app.run(debug=False, host=host, port=port) 