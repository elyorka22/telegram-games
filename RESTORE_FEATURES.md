# 🔄 Восстановление полной функциональности

## Текущее состояние

Приложение упрощено для решения проблемы с health check:
- ✅ Базовое Flask приложение работает
- ✅ Health check проходит успешно
- ❌ WebSocket отключен
- ❌ Telegram бот отключен

## Шаг 1: Проверка базового деплоя

После загрузки изменений в Git, проверьте в Railway:

1. **Health check проходит** ✅
2. **Приложение отвечает** на `/` и `/health`
3. **Логи показывают** успешный запуск

## Шаг 2: Восстановление WebSocket

После успешного базового деплоя, раскомментируйте в `app.py`:

### 1. Импорты
```python
from flask_socketio import SocketIO, emit, join_room, leave_room
from chess_game import ChessGame, Color
from checkers_game import CheckersGame, CheckerColor
import uuid
import json
import threading
```

### 2. SocketIO инициализация
```python
socketio = SocketIO(app, cors_allowed_origins="*")
```

### 3. WebSocket обработчики
Раскомментируйте все `@socketio.on` обработчики:
- `handle_connect`
- `handle_disconnect`
- `handle_find_game`
- `handle_join_game`
- `handle_make_move`
- `handle_get_valid_moves`

### 4. Запуск с SocketIO
```python
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Запуск приложения на {host}:{port}")
    socketio.run(app, debug=debug, host=host, port=port, allow_unsafe_werkzeug=True)
```

## Шаг 3: Восстановление Telegram бота

### 1. Функция запуска бота
```python
def start_telegram_bot():
    """Запуск Telegram бота в отдельном потоке"""
    try:
        from telegram_bot import TelegramGameBot
        bot = TelegramGameBot()
        bot.run()
    except Exception as e:
        logger.error(f"Ошибка запуска Telegram бота: {e}")
```

### 2. Автозапуск бота
```python
# Запускаем Telegram бота в отдельном потоке при импорте
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
if bot_token and bot_token != 'YOUR_BOT_TOKEN_HERE':
    bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
    bot_thread.start()
    logger.info("Telegram бот запущен в отдельном потоке")
else:
    logger.warning("TELEGRAM_BOT_TOKEN не установлен, бот не запущен")
```

## Шаг 4: Обновление Procfile

После восстановления WebSocket, обновите Procfile:
```
web: gunicorn --bind 0.0.0.0:$PORT --worker-class eventlet --workers 1 app:app
```

## Шаг 5: Тестирование

### Локальное тестирование
```bash
# Тест базового приложения
python test_simple.py

# Тест с WebSocket
python app.py
```

### Проверка в Railway
1. Загрузите изменения в Git
2. Проверьте логи: `railway logs`
3. Проверьте health check
4. Протестируйте WebSocket соединения

## Порядок восстановления

1. **Сначала** убедитесь, что базовое приложение работает
2. **Затем** восстановите WebSocket
3. **Потом** восстановите Telegram бота
4. **Наконец** протестируйте полную функциональность

## Откат при проблемах

Если что-то не работает, можно быстро откатиться к рабочей версии:
```bash
git checkout HEAD~1
git push origin main --force
```

## Полезные команды

```bash
# Проверка статуса
git status

# Просмотр изменений
git diff

# Отмена изменений в файле
git checkout -- app.py

# Принудительный откат
git reset --hard HEAD~1
``` 