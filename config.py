import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Конфигурация Telegram бота
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'http://localhost:5000')

# Конфигурация Flask приложения
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'chess_secret_key_2024')
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# Конфигурация WebSocket
SOCKETIO_CORS_ALLOWED_ORIGINS = os.getenv('SOCKETIO_CORS_ALLOWED_ORIGINS', '*')

# Конфигурация игр
MAX_GAME_DURATION = int(os.getenv('MAX_GAME_DURATION', 3600))  # 1 час
CLEANUP_INTERVAL = int(os.getenv('CLEANUP_INTERVAL', 300))  # 5 минут 