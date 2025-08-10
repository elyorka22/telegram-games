#!/usr/bin/env python3
"""
Скрипт для проверки здоровья приложения
Используется Railway для health check
"""

import requests
import sys
import os

def check_health():
    """Проверка здоровья приложения"""
    try:
        # Получаем URL из переменных окружения или используем localhost
        base_url = os.getenv('WEBAPP_URL', 'http://localhost:5000')
        
        # Проверяем основной endpoint
        response = requests.get(f"{base_url}/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Приложение работает корректно")
            return True
        else:
            print(f"❌ Приложение вернуло статус {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

if __name__ == "__main__":
    success = check_health()
    sys.exit(0 if success else 1) 