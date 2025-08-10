#!/usr/bin/env python3
"""
WSGI приложение для запуска с gunicorn в Railway
"""

import os
import threading
import time
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

# Конфигурация для Railway
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'http://localhost:5000')
PORT = int(os.getenv('PORT', 5000))
HOST = os.getenv('HOST', '0.0.0.0')

def start_telegram_bot():
    """Запуск Telegram бота в отдельном потоке"""
    try:
        from telegram_bot import TelegramGameBot
        bot = TelegramGameBot()
        bot.run()
    except Exception as e:
        logger.error(f"Ошибка запуска Telegram бота: {e}")

def start_flask_app():
    """Запуск Flask приложения"""
    try:
        from app import app, socketio
        socketio.run(app, debug=False, host=HOST, port=PORT, allow_unsafe_werkzeug=True)
    except Exception as e:
        logger.error(f"Ошибка запуска Flask приложения: {e}")

# Запускаем Telegram бота в отдельном потоке
if BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE':
    bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
    bot_thread.start()
    logger.info("Telegram бот запущен в отдельном потоке")
else:
    logger.warning("TELEGRAM_BOT_TOKEN не установлен, бот не запущен")

# Импортируем Flask приложение
from app import app

# Экспортируем WSGI приложение
application = app

if __name__ == '__main__':
    logger.info(f"Запуск приложения на {HOST}:{PORT}")
    logger.info(f"WebApp URL: {WEBAPP_URL}")
    
    # Запускаем Flask приложение
    start_flask_app() 