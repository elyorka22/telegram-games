from flask import Flask, jsonify, request
import os
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Конфигурация
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://telegram-games-two.vercel.app')

@app.route('/', methods=['GET'])
def index():
    """Главная страница API"""
    return jsonify({
        'message': 'Telegram Games API is running on Vercel!',
        'status': 'ok',
        'platform': 'vercel',
        'bot_configured': bool(BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE'),
        'webapp_url': WEBAPP_URL
    })

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
            '/api/test',
            '/api/test-bot',
            '/api/webhook',
            '/api/webhook/setup',
            '/api/webhook/status'
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
        'version': '1.0.0',
        'bot_configured': bool(BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE')
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

@app.route('/api/test-bot', methods=['GET'])
def test_bot():
    """Тестовый endpoint для проверки бота"""
    return jsonify({
        'message': 'Bot Test Endpoint',
        'status': 'running',
        'bot_token_configured': bool(BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE'),
        'bot_token_length': len(BOT_TOKEN) if BOT_TOKEN else 0,
        'webapp_url': WEBAPP_URL,
        'environment_variables': {
            'TELEGRAM_BOT_TOKEN': '***' if BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE' else 'NOT_SET',
            'WEBAPP_URL': WEBAPP_URL
        }
    })

@app.route('/api/webhook', methods=['GET'])
def webhook_info():
    """Информация о webhook"""
    webhook_url = f"{WEBAPP_URL}/api/webhook"
    return jsonify({
        'webhook_url': webhook_url,
        'webhook_setup_url': f"{WEBAPP_URL}/api/webhook/setup",
        'webhook_status_url': f"{WEBAPP_URL}/api/webhook/status",
        'bot_configured': bool(BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE')
    })

@app.route('/api/webhook/setup', methods=['GET'])
def setup_webhook():
    """Настройка webhook для бота"""
    if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        return jsonify({'error': 'Bot token not configured'}), 400
    
    try:
        # Здесь должна быть логика настройки webhook
        # Пока возвращаем информацию
        webhook_url = f"{WEBAPP_URL}/api/webhook"
        return jsonify({
            'status': 'ok',
            'message': 'Webhook setup endpoint',
            'webhook_url': webhook_url,
            'bot_token_configured': True
        }), 200
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhook/status', methods=['GET'])
def webhook_status():
    """Статус webhook"""
    if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        return jsonify({'error': 'Bot token not configured'}), 400
    
    try:
        return jsonify({
            'status': 'ok',
            'message': 'Webhook status endpoint',
            'bot_configured': True,
            'webhook_url': f"{WEBAPP_URL}/api/webhook"
        }), 200
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        return jsonify({'error': str(e)}), 500

# Export the Flask app for Vercel
app.debug = False 