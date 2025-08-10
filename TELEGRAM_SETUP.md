# 🤖 Настройка Telegram бота

Подробная инструкция по созданию и настройке Telegram бота для игр в шахматы и шашки.

## 📋 Шаг 1: Создание бота

### 1.1 Найдите @BotFather
1. Откройте Telegram
2. Найдите пользователя `@BotFather`
3. Нажмите "Start" или отправьте `/start`

### 1.2 Создайте нового бота
1. Отправьте команду `/newbot`
2. Введите имя бота (например: "Игровой Бот")
3. Введите username бота (например: "my_games_bot")
   - Username должен заканчиваться на `bot`
   - Должен быть уникальным
4. Сохраните полученный токен!

### 1.3 Настройте описание бота
```
/setdescription
@your_bot_username
Играйте в шахматы и шашки онлайн! Находите противников и сражайтесь в реальном времени.
```

## 📋 Шаг 2: Настройка Mini App

### 2.1 Настройте кнопку меню
1. Отправьте команду `/setmenubutton`
2. Выберите вашего бота
3. Введите текст кнопки: `🎮 Играть в игры`
4. Введите URL: `http://localhost:5000` (для тестирования)
   - Для продакшена: `https://your-domain.com`

### 2.2 Альтернативный способ через BotFather
```
/setmenubutton
@your_bot_username
🎮 Играть в игры
http://localhost:5000
```

## 📋 Шаг 3: Настройка команд

### 3.1 Установите команды бота
```
/setcommands
@your_bot_username
start - 🎮 Главное меню
games - 🎯 Выбор игры
help - 📖 Справка по играм
```

## 📋 Шаг 4: Конфигурация приложения

### 4.1 Создайте файл .env
```bash
# Создайте файл .env в корне проекта
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
WEBAPP_URL=http://localhost:5000
FLASK_SECRET_KEY=your_secret_key_here
```

### 4.2 Получите токен
- Токен был выдан при создании бота
- Формат: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
- Храните токен в секрете!

## 📋 Шаг 5: Запуск бота

### 5.1 Запустите Telegram бота
```bash
python telegram_bot.py
```

### 5.2 Проверьте работу
1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Нажмите кнопку "🎮 Играть в игры"

## 📋 Шаг 6: Продакшн настройка

### 6.1 Настройте домен
1. Получите домен (например, через ngrok или хостинг)
2. Настройте SSL сертификат
3. Обновите URL в .env файле

### 6.2 Обновите BotFather
```
/setmenubutton
@your_bot_username
🎮 Играть в игры
https://your-domain.com
```

### 6.3 Настройте вебхуки (опционально)
```python
# В telegram_bot.py добавьте:
application.run_webhook(
    listen='0.0.0.0',
    port=8443,
    url_path='',
    webhook_url='https://your-domain.com/webhook'
)
```

## 🔧 Команды BotFather

### Основные команды:
- `/newbot` - Создать нового бота
- `/mybots` - Список ваших ботов
- `/setdescription` - Установить описание
- `/setabouttext` - Установить информацию о боте
- `/setmenubutton` - Настроить кнопку меню
- `/setcommands` - Установить команды
- `/setuserpic` - Установить аватар бота

### Настройка Mini App:
- `/setmenubutton` - Основная команда для настройки
- URL должен быть HTTPS для продакшена
- Поддерживаются параметры: `?game=chess`, `?game=checkers`

## 🧪 Тестирование

### Локальное тестирование:
1. Запустите `python telegram_bot.py`
2. Откройте бота в Telegram
3. Нажмите кнопку "🎮 Играть в игры"
4. Проверьте работу игр

### Тестирование с ngrok:
```bash
# Установите ngrok
brew install ngrok  # macOS
# или скачайте с https://ngrok.com

# Запустите туннель
ngrok http 5000

# Скопируйте HTTPS URL и обновите BotFather
/setmenubutton
@your_bot_username
🎮 Играть в игры
https://abc123.ngrok.io
```

## 🚨 Частые проблемы

### 1. "Bot not found"
- Проверьте правильность username
- Убедитесь, что бот создан

### 2. "Invalid token"
- Проверьте токен в .env файле
- Убедитесь, что токен скопирован полностью

### 3. "Web App not loading"
- Проверьте URL в BotFather
- Убедитесь, что приложение запущено
- Проверьте доступность по URL

### 4. "Mini App not working"
- Проверьте консоль браузера на ошибки
- Убедитесь, что Telegram Web App JS загружен
- Проверьте WebSocket соединение

## 📱 Telegram Mini App API

### Основные методы:
```javascript
// Инициализация
window.Telegram.WebApp.ready();

// Настройка темы
window.Telegram.WebApp.setHeaderColor('#2481cc');

// Показать уведомление
window.Telegram.WebApp.showAlert('Сообщение');

// Закрыть приложение
window.Telegram.WebApp.close();
```

### События:
```javascript
// Изменение темы
window.Telegram.WebApp.onEvent('themeChanged', function() {
    // Обновить UI
});

// Изменение viewport
window.Telegram.WebApp.onEvent('viewportChanged', function() {
    // Адаптировать размер
});
```

## 🎯 Готово!

После выполнения всех шагов у вас будет:
- ✅ Работающий Telegram бот
- ✅ Mini App с играми в шахматы и шашки
- ✅ Real-time игровой процесс
- ✅ Адаптивный дизайн под Telegram

**Удачной игры! 🎮** 