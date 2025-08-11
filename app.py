from flask import Flask, jsonify, render_template, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Главная страница"""
    try:
        return render_template('index.html')
    except:
        return jsonify({
            'message': 'Telegram Games App is running on Vercel!',
            'status': 'ok',
            'platform': 'vercel'
        })

@app.route('/game')
def game():
    """Страница игры"""
    try:
        # Генерируем случайный ID игры для демонстрации
        import uuid
        game_id = str(uuid.uuid4())[:8]
        return render_template('game.html', game_id=game_id)
    except Exception as e:
        return jsonify({
            'message': 'Game page',
            'status': 'ok',
            'platform': 'vercel',
            'error': str(e)
        })

@app.route('/health')
def health_check():
    """Health check endpoint для Vercel"""
    return jsonify({
        'status': 'healthy',
        'message': 'Application is running on Vercel',
        'platform': 'vercel'
    }), 200

@app.route('/test')
def test():
    """Тестовый endpoint"""
    return jsonify({
        'message': 'Test endpoint working on Vercel!',
        'status': 'ok',
        'platform': 'vercel'
    }), 200

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'running',
        'environment': os.getenv('VERCEL_ENV', 'development'),
        'region': os.getenv('VERCEL_REGION', 'unknown'),
        'platform': 'vercel'
    })

@app.route('/api/health')
def api_health():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'message': 'API is running on Vercel',
        'platform': 'vercel'
    }), 200

@app.route('/api/test')
def api_test():
    """API test endpoint"""
    return jsonify({
        'message': 'API test endpoint working on Vercel!',
        'status': 'ok',
        'platform': 'vercel'
    }), 200

@app.route('/static/<path:filename>')
def static_files(filename):
    """Обработка статических файлов"""
    return send_from_directory('static', filename)

@app.errorhandler(404)
def not_found(error):
    """Обработка 404 ошибок"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found',
        'status': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Обработка 500 ошибок"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on the server',
        'status': 500
    }), 500

# Для локального запуска
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = '0.0.0.0'
    
    print(f"Starting app on {host}:{port}")
    print(f"PORT environment variable: {os.getenv('PORT')}")
    app.run(debug=False, host=host, port=port) 