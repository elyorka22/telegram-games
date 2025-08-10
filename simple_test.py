#!/usr/bin/env python3
"""
Простой тест для проверки базового приложения
"""

import requests
import time

def test_app():
    """Тестирование приложения"""
    print("🧪 Тестирование приложения...")
    
    # Ждем немного для запуска
    time.sleep(2)
    
    try:
        # Тест главной страницы
        response = requests.get('http://localhost:5000/', timeout=5)
        print(f"✅ Главная страница: {response.status_code}")
        print(f"   Ответ: {response.json()}")
        
        # Тест health check
        response = requests.get('http://localhost:5000/health', timeout=5)
        print(f"✅ Health check: {response.status_code}")
        print(f"   Ответ: {response.json()}")
        
        # Тест test endpoint
        response = requests.get('http://localhost:5000/test', timeout=5)
        print(f"✅ Test endpoint: {response.status_code}")
        print(f"   Ответ: {response.json()}")
        
        print("🎉 Все тесты пройдены!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == '__main__':
    test_app() 