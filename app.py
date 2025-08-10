from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Главная страница"""
    return jsonify({
        'message': 'Telegram Games App is running!',
        'status': 'ok'
    })

@app.route('/health')
def health_check():
    """Health check endpoint для Railway"""
    return jsonify({
        'status': 'healthy',
        'message': 'Application is running'
    }), 200

@app.route('/test')
def test():
    """Тестовый endpoint"""
    return jsonify({
        'message': 'Test endpoint working!',
        'status': 'ok'
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"Starting app on {host}:{port}")
    app.run(debug=False, host=host, port=port) 