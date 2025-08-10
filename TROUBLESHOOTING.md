# 🔧 Устранение проблем деплоя

## Проблема: Health Check не проходит

### Симптомы:
- Логи показывают "service unavailable"
- Health check не может подключиться к `/` или `/health`

### Решения:

#### 1. Проверьте переменные окружения
Убедитесь, что в Railway установлены:
```
TELEGRAM_BOT_TOKEN=ваш_токен_бота
WEBAPP_URL=https://ваш-проект.railway.app
```

#### 2. Проверьте логи приложения
```bash
railway logs
```

#### 3. Перезапустите приложение
```bash
railway up
```

## Проблема: Приложение не запускается

### Симптомы:
- Ошибки импорта
- Ошибки зависимостей
- Приложение падает при старте

### Решения:

#### 1. Проверьте requirements.txt
Убедитесь, что все зависимости указаны:
```
Flask==3.1.1
Flask-SocketIO==5.5.1
python-telegram-bot==21.7
python-dotenv==1.0.0
gunicorn==21.2.0
eventlet==0.35.2
```

#### 2. Проверьте версию Python
В `runtime.txt` должна быть:
```
python-3.11.7
```

#### 3. Проверьте Procfile
Должен содержать:
```
web: gunicorn --bind 0.0.0.0:$PORT --worker-class eventlet --workers 1 app:app
```

## Проблема: Telegram бот не отвечает

### Симптомы:
- Бот не отвечает на команды
- Ошибки в логах бота

### Решения:

#### 1. Проверьте токен бота
- Убедитесь, что `TELEGRAM_BOT_TOKEN` правильный
- Проверьте, что бот не заблокирован

#### 2. Проверьте настройки бота
- В @BotFather проверьте, что бот активен
- Убедитесь, что нет ограничений

#### 3. Проверьте логи
```bash
railway logs --follow
```

## Проблема: WebApp не открывается

### Симптомы:
- Кнопка в Telegram не работает
- WebApp не загружается

### Решения:

#### 1. Проверьте WEBAPP_URL
Убедитесь, что URL правильный:
```
WEBAPP_URL=https://ваш-проект.railway.app
```

#### 2. Настройте Menu Button
В @BotFather:
1. `/mybots`
2. Выберите бота
3. Bot Settings → Menu Button
4. URL: `https://ваш-проект.railway.app`

#### 3. Проверьте доступность
Откройте URL в браузере - должно загрузиться приложение

## Проблема: Игры не работают

### Симптомы:
- WebSocket ошибки
- Игроки не могут подключиться

### Решения:

#### 1. Проверьте WebSocket
Убедитесь, что eventlet работает:
```bash
railway logs | grep socket
```

#### 2. Проверьте CORS
В app.py должно быть:
```python
socketio = SocketIO(app, cors_allowed_origins="*")
```

#### 3. Проверьте порт
Убедитесь, что приложение слушает правильный порт:
```python
port = int(os.getenv('PORT', 5000))
```

## Полезные команды

### Просмотр логов
```bash
# Все логи
railway logs

# Логи в реальном времени
railway logs --follow

# Логи конкретного сервиса
railway logs --service web
```

### Управление приложением
```bash
# Перезапуск
railway up

# Проверка статуса
railway status

# Переменные окружения
railway variables
```

### Отладка
```bash
# Проверка локально
python3 check_deployment.py

# Запуск локально
python3 start_local.py

# Проверка здоровья
python3 healthcheck.py
```

## Частые ошибки

### 1. "ModuleNotFoundError"
**Решение**: Проверьте requirements.txt и перезапустите

### 2. "Connection refused"
**Решение**: Проверьте переменные окружения и перезапустите

### 3. "Bot token invalid"
**Решение**: Проверьте TELEGRAM_BOT_TOKEN

### 4. "Port already in use"
**Решение**: Railway автоматически назначит порт, используйте $PORT

## Контакты

При возникновении проблем:
1. Проверьте логи: `railway logs`
2. Проверьте документацию: [DEPLOYMENT.md](DEPLOYMENT.md)
3. Создайте issue в репозитории 