#!/usr/bin/env python3
"""
Скрипт для локального запуска приложения
Используется для тестирования перед деплоем
"""

import os
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

def main():
    """Главная функция для локального запуска"""
    print("🚀 Запуск приложения в локальном режиме...")
    
    # Проверяем наличие обязательных переменных
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token or bot_token == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Ошибка: TELEGRAM_BOT_TOKEN не установлен")
        print("Создайте файл .env и добавьте TELEGRAM_BOT_TOKEN=your_token_here")
        sys.exit(1)
    
    # Устанавливаем локальные переменные
    os.environ['WEBAPP_URL'] = 'http://localhost:5000'
    os.environ['FLASK_DEBUG'] = 'True'
    os.environ['HOST'] = '127.0.0.1'
    os.environ['PORT'] = '5000'
    
    print("✅ Переменные окружения настроены")
    print(f"🌐 WebApp URL: {os.environ['WEBAPP_URL']}")
    print(f"🔧 Debug режим: {os.environ['FLASK_DEBUG']}")
    
    # Запускаем основное приложение
    try:
        from telegram_bot import main as run_app
        run_app()
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 