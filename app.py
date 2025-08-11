from flask import Flask, render_template, send_from_directory, jsonify, request
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)

# Конфигурация
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://telegram-games-two.vercel.app')

@app.route('/')
def index():
    """Главная страница с играми"""
    return render_template('index.html')

@app.route('/game')
def game():
    """Страница игры"""
    game_id = request.args.get('game_id')
    game_type = request.args.get('type', 'chess')
    return render_template('game.html', game_id=game_id, game_type=game_type)

@app.route('/static/<path:filename>')
def static_files(filename):
    """Обработка статических файлов"""
    return send_from_directory('static', filename)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Telegram Games App is running',
        'platform': 'vercel'
    })

@app.route('/test')
def test():
    """Test endpoint"""
    return jsonify({
        'message': 'Test endpoint working!',
        'status': 'ok'
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'running',
        'bot_configured': bool(BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE'),
        'webapp_url': WEBAPP_URL
    })

@app.route('/api/bot/status')
def bot_status():
    """Bot status endpoint"""
    return jsonify({
        'bot_configured': bool(BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE'),
        'webapp_url': WEBAPP_URL,
        'platform': 'vercel'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True) 