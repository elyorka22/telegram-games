#!/usr/bin/env python3
"""
Тест для онлайн шахмат
"""

import requests
import json
import time

def test_main_page():
    """Тест главной страницы"""
    print("🧪 Тестирование главной страницы...")
    
    try:
        response = requests.get('http://localhost:5000')
        assert response.status_code == 200
        assert 'Онлайн Шахматы' in response.text
        assert 'Найти игру' in response.text
        print("✅ Главная страница работает корректно")
        return True
    except Exception as e:
        print(f"❌ Ошибка главной страницы: {e}")
        return False

def test_static_files():
    """Тест статических файлов"""
    print("🧪 Тестирование статических файлов...")
    
    static_files = [
        '/static/css/style.css',
        '/static/css/chess.css',
        '/static/js/main.js',
        '/static/js/game.js'
    ]
    
    for file_path in static_files:
        try:
            response = requests.get(f'http://localhost:5000{file_path}')
            assert response.status_code == 200
            print(f"✅ {file_path} загружается корректно")
        except Exception as e:
            print(f"❌ Ошибка загрузки {file_path}: {e}")
            return False
    
    return True

def test_chess_logic():
    """Тест логики шахмат"""
    print("🧪 Тестирование логики шахмат...")
    
    try:
        # Импортируем логику шахмат
        from chess_game import ChessGame, Color, PieceType
        
        # Создаем новую игру
        game = ChessGame("player1", "player2")
        
        # Проверяем начальную расстановку
        assert game.board[0][0] is not None  # Ладья в углу
        assert game.board[1][0] is not None  # Пешка
        assert game.board[6][0] is not None  # Белая пешка
        assert game.board[7][0] is not None  # Белая ладья
        
        # Проверяем первый ход
        assert game.current_turn == Color.WHITE
        
        # Тестируем валидный ход
        valid_move = game.is_valid_move((6, 0), (5, 0))  # Пешка e2-e3
        assert valid_move == True
        
        # Выполняем ход
        success = game.make_move((6, 0), (5, 0))
        assert success == True
        assert game.current_turn == Color.BLACK
        
        print("✅ Логика шахмат работает корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка логики шахмат: {e}")
        return False

def test_websocket_connection():
    """Тест WebSocket соединения"""
    print("🧪 Тестирование WebSocket соединения...")
    
    try:
        import socketio
        
        # Создаем клиент
        sio = socketio.Client()
        
        connected = False
        
        @sio.event
        def connect():
            nonlocal connected
            connected = True
            print("✅ WebSocket соединение установлено")
        
        @sio.event
        def disconnect():
            print("📡 WebSocket соединение разорвано")
        
        # Подключаемся к серверу
        sio.connect('http://localhost:5000')
        
        # Ждем подключения
        time.sleep(1)
        
        if connected:
            sio.disconnect()
            return True
        else:
            print("❌ Не удалось установить WebSocket соединение")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка WebSocket: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Начинаем тестирование онлайн шахмат...")
    print("=" * 50)
    
    tests = [
        test_main_page,
        test_static_files,
        test_chess_logic,
        test_websocket_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте: {e}")
    
    print("=" * 50)
    print(f"📊 Результаты тестирования: {passed}/{total} тестов прошли")
    
    if passed == total:
        print("🎉 Все тесты прошли успешно! Приложение готово к использованию.")
    else:
        print("⚠️ Некоторые тесты не прошли. Проверьте логи выше.")
    
    return passed == total

if __name__ == "__main__":
    main() 