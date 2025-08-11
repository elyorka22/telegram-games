from flask import Flask, jsonify
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)

# Конфигурация
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://your-app-name.vercel.app')

@app.route('/', methods=['GET'])
def index():
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

@app.route('/test-webhook', methods=['GET'])
def test_webhook():
    """Тест webhook URL"""
    webhook_url = f"{WEBAPP_URL}/api/webhook"
    return jsonify({
        'webhook_url': webhook_url,
        'webhook_setup_url': f"{WEBAPP_URL}/api/webhook/setup",
        'webhook_status_url': f"{WEBAPP_URL}/api/webhook/status"
    })

# Export the Flask app for Vercel
app.debug = False 