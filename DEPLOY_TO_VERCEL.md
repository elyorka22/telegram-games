# 🚀 Деплой на Vercel - Пошаговая инструкция

## ✅ Подготовка завершена!

Проект полностью готов к деплою на Vercel. Все необходимые файлы конфигурации созданы и протестированы.

## 📁 Созданные файлы конфигурации

- ✅ `vercel.json` - конфигурация Vercel с правильной маршрутизацией
- ✅ `requirements.txt` - Python зависимости (упрощены для совместимости)
- ✅ `runtime.txt` - версия Python 3.11
- ✅ `.vercelignore` - исключения для деплоя
- ✅ `api/index.py` - API endpoints для Vercel serverless функций
- ✅ `package.json` - метаданные проекта
- ✅ `app.py` - обновленное Flask приложение с поддержкой Vercel

## 🧪 Тестирование

Все endpoints протестированы и работают корректно:
- ✅ `/` - Главная страница (HTML)
- ✅ `/health` - Health check (JSON)
- ✅ `/test` - Test endpoint (JSON)
- ✅ `/game` - Страница игры (HTML)

## 🚀 Способы деплоя

### Вариант 1: Vercel CLI (рекомендуется)

```bash
# 1. Установите Vercel CLI
npm i -g vercel

# 2. Войдите в аккаунт Vercel
vercel login

# 3. Задеплойте проект
vercel

# 4. Для продакшн деплоя
vercel --prod
```

### Вариант 2: GitHub интеграция

1. Загрузите код в GitHub репозиторий
2. Зайдите на [vercel.com](https://vercel.com)
3. Нажмите "New Project"
4. Выберите ваш репозиторий
5. Vercel автоматически определит настройки
6. Нажмите "Deploy"

### Вариант 3: Vercel Dashboard

1. Зайдите на [vercel.com](https://vercel.com)
2. Нажмите "New Project"
3. Выберите "Upload" и загрузите ZIP архив проекта
4. Vercel автоматически настроит деплой

## 📋 Что будет доступно после деплоя

### Основные страницы
- `/` - Главная страница с выбором игр
- `/game` - Страница игры с доской

### API Endpoints
- `/health` - Health check
- `/test` - Тестовый endpoint
- `/api/status` - API статус
- `/api/health` - API health check
- `/api/test` - API тест

### Статические файлы
- `/static/css/*` - CSS стили
- `/static/js/*` - JavaScript файлы

## 🔧 Конфигурация Vercel

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    },
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/index.py"
    },
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "FLASK_ENV": "production"
  },
  "functions": {
    "app.py": {
      "maxDuration": 30
    },
    "api/index.py": {
      "maxDuration": 30
    }
  }
}
```

### requirements.txt
```
Flask>=3.1.0
gunicorn>=21.0.0
requests>=2.31.0
```

## 🌐 Переменные окружения

При необходимости добавьте в настройках проекта на Vercel:

- `FLASK_ENV=production`
- `VERCEL_ENV=production`

## 📊 Мониторинг

После деплоя вы сможете:

1. **Отслеживать логи** в Vercel Dashboard
2. **Настроить алерты** для ошибок
3. **Мониторить производительность** 
4. **Настроить домен** для проекта
5. **Просматривать аналитику** трафика

## 🔄 Обновление

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

## 🛠️ Troubleshooting

### Проблемы с деплоем
1. Проверьте логи в Vercel Dashboard
2. Убедитесь, что все зависимости указаны в `requirements.txt`
3. Проверьте, что версия Python в `runtime.txt` поддерживается

### Проблемы с производительностью
1. Оптимизируйте размер статических файлов
2. Используйте кэширование
3. Настройте CDN для статических файлов

## 🎉 Готово к деплою!

Проект полностью настроен и готов к деплою на Vercel. Выберите любой из предложенных способов деплоя и наслаждайтесь вашим приложением в облаке!

---

**Следующий шаг:** Выполните команду `vercel` в корне проекта для деплоя. 