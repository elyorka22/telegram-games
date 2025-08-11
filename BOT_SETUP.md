# 🤖 Настройка Telegram бота для Vercel

## ✅ Шаг 1: Создание бота в Telegram

1. **Найдите @BotFather в Telegram**
2. **Отправьте команду:** `/newbot`
3. **Введите имя бота:** например, "Telegram Games Bot"
4. **Введите username бота:** например, "telegram_games_bot"
5. **Получите токен бота** (выглядит как `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## 🔧 Шаг 2: Настройка переменных окружения в Vercel

### Через Vercel Dashboard:

1. **Зайдите в ваш проект на [vercel.com](https://vercel.com)**
2. **Перейдите в Settings → Environment Variables**
3. **Добавьте следующие переменные:**

```
TELEGRAM_BOT_TOKEN=ваш_токен_бота_здесь
WEBAPP_URL=https://ваш-проект.vercel.app
```

### Через Vercel CLI:

```bash
# Добавить переменные окружения
vercel env add TELEGRAM_BOT_TOKEN
vercel env add WEBAPP_URL

# Или добавить все сразу
vercel env pull .env.local
# Отредактируйте .env.local и загрузите обратно
vercel env push
```

## 🌐 Шаг 3: Настройка WebApp URL

1. **Получите URL вашего приложения на Vercel**
2. **Установите переменную `WEBAPP_URL`:**
   ```
   WEBAPP_URL=https://ваш-проект.vercel.app
   ```

## 🤖 Шаг 4: Настройка бота для WebApp

1. **Отправьте @BotFather команду:** `/setmenubutton`
2. **Выберите вашего бота**
3. **Введите URL вашего WebApp:** `https://ваш-проект.vercel.app`
4. **Или используйте команду:** `/setcommands`
5. **Добавьте команды:**
   ```
   start - Начать игру
   games - Выбрать игру
   help - Справка
   ```

## 🔗 Шаг 5: Настройка Webhook

После деплоя настройте webhook для автоматических сообщений:

```bash
# Настройка webhook
curl https://ваш-проект.vercel.app/api/webhook/setup

# Проверка статуса webhook
curl https://ваш-проект.vercel.app/api/webhook/status
```

## 🧪 Шаг 6: Тестирование

### Проверьте статус бота:

```bash
curl https://ваш-проект.vercel.app/api/bot/status
```

Ожидаемый ответ:
```json
{
  "bot_configured": true,
  "webapp_url": "https://ваш-проект.vercel.app",
  "platform": "vercel"
}
```

### Проверьте webhook:

```bash
curl https://ваш-проект.vercel.app/api/webhook
```

### Проверьте в Telegram:

1. **Найдите вашего бота в Telegram**
2. **Отправьте команду:** `/start`
3. **Бот должен ответить приветственным сообщением с кнопкой**
4. **Нажмите кнопку "🎮 Играть в игры"**
5. **Должно открыться WebApp с играми**

## 🔄 Шаг 7: Перезапуск деплоя

После добавления переменных окружения:

```bash
# Перезапустите деплой
vercel --prod
```

Или через Dashboard:
1. **Перейдите в Deployments**
2. **Нажмите "Redeploy"**

## 📋 Пример переменных окружения

Создайте файл `.env.local` (не загружайте в Git):

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
WEBAPP_URL=https://your-app-name.vercel.app

# Flask Application Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_DEBUG=False

# Game Configuration
MAX_GAME_DURATION=3600
CLEANUP_INTERVAL=300
```

## 🎯 Что будет работать после настройки:

### Автоматические сообщения:
- ✅ `/start` - приветственное сообщение с кнопкой
- ✅ `/games` - выбор игры с кнопками
- ✅ `/help` - справка по боту
- ✅ Кнопки для открытия WebApp

### WebApp:
- ✅ Открытие игр в Telegram
- ✅ Шахматы и шашки
- ✅ Полная функциональность

## 🛠️ Troubleshooting

### Бот не отвечает:
1. Проверьте токен в переменных окружения
2. Убедитесь, что webhook настроен
3. Проверьте логи в Vercel Dashboard
4. Выполните: `curl https://ваш-проект.vercel.app/api/webhook/setup`

### WebApp не открывается:
1. Проверьте URL в переменной `WEBAPP_URL`
2. Убедитесь, что приложение работает
3. Проверьте настройки бота в @BotFather

### Ошибки деплоя:
1. Проверьте логи в Vercel Dashboard
2. Убедитесь, что все зависимости установлены
3. Проверьте синтаксис переменных окружения

## 🎉 Готово!

После выполнения всех шагов ваш Telegram бот будет:
- ✅ Отвечать на команды автоматически
- ✅ Отправлять приветственные сообщения
- ✅ Показывать кнопки для игр
- ✅ Открывать WebApp с играми

---

**Полезные ссылки:**
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram WebApp](https://core.telegram.org/bots/webapps)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables) 