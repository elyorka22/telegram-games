#!/usr/bin/env python3
"""
Простой скрипт для запуска веб-приложения без Telegram бота
"""

import os
import sys
from app import app, socketio

def main():
    """Запуск Flask приложения"""
    print("🎮 Запуск онлайн игр (шахматы и шашки)")
    print("📍 URL: http://localhost:5000")
    print("⚡ WebSocket: ws://localhost:5000")
    print("🔄 Нажмите Ctrl+C для остановки")
    print("-" * 50)
    
    try:
        # Запускаем приложение
        socketio.run(
            app, 
            debug=True, 
            host='0.0.0.0', 
            port=5000,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Приложение остановлено")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 