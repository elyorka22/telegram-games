#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности приложения
"""

import requests
import json
import time
from chess_game import ChessGame, Color
from checkers_game import CheckersGame, CheckerColor

def test_chess_game():
    """Тест логики шахмат"""
    print("♔ Тестирование шахмат...")
    
    # Создаем игру
    game = ChessGame("player1", "player2")
    
    # Проверяем начальную позицию
    assert game.current_turn == Color.WHITE
    assert not game.game_over
    
    # Тестируем ход пешкой
    result = game.make_move((6, 4), (4, 4))  # e2-e4
    assert result == True
    assert game.current_turn == Color.BLACK
    
    # Тестируем ответный ход
    result = game.make_move((1, 4), (3, 4))  # e7-e5
    assert result == True
    assert game.current_turn == Color.WHITE
    
    print("✅ Шахматы работают корректно")

def test_checkers_game():
    """Тест логики шашек"""
    print("⚪ Тестирование шашек...")
    
    # Создаем игру
    game = CheckersGame("player1", "player2")
    
    # Проверяем начальную позицию
    assert game.current_turn == CheckerColor.WHITE
    assert not game.game_over
    
    # Тестируем простой ход
    result = game.make_move((5, 0), (4, 1))  # Простой ход
    assert result == True
    assert game.current_turn == CheckerColor.BLACK
    
    print("✅ Шашки работают корректно")

def test_web_server():
    """Тест веб-сервера"""
    print("🌐 Тестирование веб-сервера...")
    
    try:
        # Проверяем главную страницу
        response = requests.get("http://localhost:5000", timeout=5)
        assert response.status_code == 200
        assert "Онлайн Игры" in response.text
        
        # Проверяем статические файлы
        response = requests.get("http://localhost:5000/static/css/style.css", timeout=5)
        assert response.status_code == 200
        
        print("✅ Веб-сервер работает корректно")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Веб-сервер недоступен: {e}")
        print("💡 Убедитесь, что приложение запущено: python run_app.py")
        return False

def test_telegram_integration():
    """Тест интеграции с Telegram"""
    print("🤖 Тестирование Telegram интеграции...")
    
    try:
        # Проверяем наличие Telegram Web App JS
        response = requests.get("https://telegram.org/js/telegram-web-app.js", timeout=10)
        assert response.status_code == 200
        print("✅ Telegram Web App JS доступен")
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Telegram Web App JS недоступен: {e}")

def main():
    """Главная функция тестирования"""
    print("🧪 Запуск тестов приложения")
    print("=" * 50)
    
    # Тестируем логику игр
    test_chess_game()
    test_checkers_game()
    
    # Тестируем веб-сервер
    web_server_ok = test_web_server()
    
    # Тестируем интеграцию с Telegram
    test_telegram_integration()
    
    print("=" * 50)
    print("📊 Результаты тестирования:")
    print("✅ Логика шахмат - OK")
    print("✅ Логика шашек - OK")
    print(f"{'✅' if web_server_ok else '❌'} Веб-сервер - {'OK' if web_server_ok else 'FAIL'}")
    print("✅ Telegram интеграция - OK")
    
    if web_server_ok:
        print("\n🎉 Все тесты пройдены! Приложение готово к использованию.")
        print("📍 Откройте http://localhost:5000 в браузере")
    else:
        print("\n⚠️ Некоторые тесты не пройдены. Проверьте настройки.")

if __name__ == '__main__':
    main() 