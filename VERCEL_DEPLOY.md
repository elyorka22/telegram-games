# Деплой на Vercel

## Подготовка проекта

Проект уже настроен для деплоя на Vercel. Все необходимые файлы конфигурации созданы:

- `vercel.json` - конфигурация Vercel
- `requirements.txt` - Python зависимости
- `runtime.txt` - версия Python
- `.vercelignore` - исключения для деплоя
- `api/index.py` - API endpoints
- `package.json` - метаданные проекта

## Способы деплоя

### 1. Через Vercel CLI (рекомендуется)

```bash
# Установка Vercel CLI
npm i -g vercel

# Логин в Vercel (если еще не залогинены)
vercel login

# Деплой
vercel

# Для продакшн деплоя
vercel --prod
```

### 2. Через GitHub интеграцию

1. Загрузите код в GitHub репозиторий
2. Зайдите на [vercel.com](https://vercel.com)
3. Нажмите "New Project"
4. Выберите ваш репозиторий
5. Vercel автоматически определит настройки
6. Нажмите "Deploy"

### 3. Через Vercel Dashboard

1. Зайдите на [vercel.com](https://vercel.com)
2. Нажмите "New Project"
3. Выберите "Upload" и загрузите ZIP архив проекта
4. Vercel автоматически настроит деплой

## Структура проекта

```
├── app.py              # Основное Flask приложение
├── api/index.py        # API endpoints
├── templates/          # HTML шаблоны
│   ├── index.html
│   └── game.html
├── static/             # Статические файлы
│   ├── css/
│   └── js/
├── vercel.json         # Конфигурация Vercel
├── requirements.txt    # Python зависимости
├── runtime.txt         # Версия Python
├── .vercelignore       # Исключения для деплоя
└── package.json        # Метаданные проекта
```

## Endpoints

После деплоя будут доступны следующие endpoints:

- `/` - Главная страница
- `/game` - Страница игры
- `/health` - Health check
- `/test` - Тестовый endpoint
- `/api/status` - API статус
- `/api/health` - API health check
- `/api/test` - API тест
- `/static/*` - Статические файлы

## Переменные окружения

При необходимости добавьте переменные окружения в настройках проекта на Vercel:

- `FLASK_ENV=production`
- `VERCEL_ENV=production`

## Мониторинг

После деплоя вы можете:

1. Отслеживать логи в Vercel Dashboard
2. Настроить алерты
3. Мониторить производительность
4. Настроить домен

## Troubleshooting

### Проблемы с деплоем

1. Проверьте логи в Vercel Dashboard
2. Убедитесь, что все зависимости указаны в `requirements.txt`
3. Проверьте, что версия Python в `runtime.txt` поддерживается

### Проблемы с производительностью

1. Оптимизируйте размер статических файлов
2. Используйте кэширование
3. Настройте CDN для статических файлов

## Обновление

Для обновления приложения:

```bash
# Локальные изменения
git add .
git commit -m "Update app"
git push

# Vercel автоматически пересоберет и задеплоит
```

Или через CLI:

```bash
vercel --prod
``` 