# 🚀 Быстрый деплой в Railway

## Шаг 1: Подготовка проекта

```bash
# Проверка готовности
python3 check_deployment.py

# Если все проверки пройдены, коммитим изменения
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

## Шаг 2: Создание проекта в Railway

1. Зайдите на [railway.app](https://railway.app)
2. Нажмите "New Project"
3. Выберите "Deploy from GitHub repo"
4. Выберите ваш репозиторий
5. Railway автоматически определит тип проекта

## Шаг 3: Настройка переменных окружения

В настройках проекта Railway добавьте:

### Обязательные:
- `TELEGRAM_BOT_TOKEN` = ваш_токен_бота
- `WEBAPP_URL` = https://ваш-проект.railway.app

### Опциональные:
- `FLASK_SECRET_KEY` = ваш_секретный_ключ
- `FLASK_DEBUG` = False

## Шаг 4: Настройка Telegram бота

1. Найдите @BotFather в Telegram
2. Отправьте `/mybots`
3. Выберите вашего бота
4. Bot Settings → Menu Button
5. URL: `https://ваш-проект.railway.app`

## Шаг 5: Проверка деплоя

```bash
# Установка Railway CLI
npm install -g @railway/cli

# Подключение к проекту
railway login
railway link

# Просмотр логов
railway logs

# Проверка статуса
railway status
```

## Готово! 🎉

Ваше приложение доступно по адресу: `https://ваш-проект.railway.app`

## Устранение проблем

### Бот не отвечает
- Проверьте `TELEGRAM_BOT_TOKEN`
- Убедитесь, что бот не заблокирован

### WebApp не открывается
- Проверьте `WEBAPP_URL`
- Настройте Menu Button в BotFather

### Приложение не запускается
- Проверьте логи: `railway logs`
- Убедитесь, что все переменные окружения установлены

## Полезные команды

```bash
# Перезапуск приложения
railway up

# Просмотр переменных окружения
railway variables

# Просмотр логов в реальном времени
railway logs --follow
``` 