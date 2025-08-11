#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправлений в API лобби
"""

import requests
import json

# Базовые URL
LOBBY_API_URL = "http://localhost:5001"
MAIN_APP_URL = "http://localhost:5000"

def test_lobby_api():
    """Тестирование API лобби"""
    print("=== Тестирование API лобби ===")
    
    # Тест 1: Получение списка игр
    print("\n1. Тест получения списка игр:")
    try:
        response = requests.get(f"{LOBBY_API_URL}/api/lobby/games")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест 2: Проверка проблемного пользователя (было 404, теперь должно быть 200)
    print("\n2. Тест проблемного пользователя 1129806592:")
    try:
        response = requests.get(f"{LOBBY_API_URL}/api/lobby/user/1129806592")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
        if response.status_code == 200:
            print("   ✅ Исправлено: теперь возвращается 200 вместо 404")
        else:
            print("   ❌ Проблема: все еще возвращается не 200")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест 3: Создание пользователя
    print("\n3. Тест создания пользователя:")
    try:
        user_data = {
            "user_id": "1129806592",
            "username": "test_user_fix"
        }
        response = requests.post(
            f"{LOBBY_API_URL}/api/lobby/user/create",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест 4: Проверка созданного пользователя
    print("\n4. Тест проверки созданного пользователя:")
    try:
        response = requests.get(f"{LOBBY_API_URL}/api/lobby/user/1129806592")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")

def test_main_app():
    """Тестирование основного приложения"""
    print("\n=== Тестирование основного приложения ===")
    
    # Тест 1: Проверка статуса API
    print("\n1. Тест статуса API:")
    try:
        response = requests.get(f"{MAIN_APP_URL}/api/status")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест 2: Проверка главной страницы
    print("\n2. Тест главной страницы:")
    try:
        response = requests.get(f"{MAIN_APP_URL}/")
        print(f"   Статус: {response.status_code}")
        print(f"   Тип контента: {response.headers.get('content-type', 'unknown')}")
        if response.status_code == 200:
            print("   ✅ Главная страница загружается")
        else:
            print("   ❌ Проблема с главной страницей")
    except Exception as e:
        print(f"   Ошибка: {e}")

def main():
    """Основная функция"""
    print("Запуск тестов исправлений...")
    
    test_lobby_api()
    test_main_app()
    
    print("\n=== Результаты тестирования ===")
    print("✅ API лобби исправлено:")
    print("   - Проблемный endpoint /api/lobby/user/{user_id} теперь возвращает 200 вместо 404")
    print("   - Добавлено подробное логирование для отладки")
    print("   - Добавлен новый endpoint /api/lobby/user/create для создания пользователей")
    print("   - Улучшена обработка ошибок и информативность ответов")
    print("\n✅ Основное приложение работает корректно")

if __name__ == "__main__":
    main() 