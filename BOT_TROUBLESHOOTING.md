# 🔍 Диагностика проблем с Telegram ботом

## ❌ Бот не реагирует - что делать?

### Шаг 1: Проверьте деплой

1. **Убедитесь, что последние изменения задеплоились:**
   ```bash
   # Проверьте логи в Vercel Dashboard
   # Или используйте CLI
   vercel logs
   ```

2. **Проверьте, что используется правильный коммит:**
   - Последний коммит должен быть: `27316b6`
   - Содержит webhook функциональность

### Шаг 2: Проверьте переменные окружения

1. **В Vercel Dashboard → Settings → Environment Variables:**
   ```
   TELEGRAM_BOT_TOKEN=ваш_токен_бота_здесь
   WEBAPP_URL=https://ваш-проект.vercel.app
   ```

2. **Проверьте через тестовый endpoint:**
   ```bash
   curl https://ваш-проект.vercel.app/api/test-bot
   ```

   Ожидаемый ответ:
   ```json
   {
     "bot_token_configured": true,
     "bot_token_length": 46,
     "webapp_url": "https://ваш-проект.vercel.app"
   }
   ```

### Шаг 3: Настройте webhook

1. **Настройте webhook:**
   ```bash
   curl https://ваш-проект.vercel.app/api/webhook/setup
   ```

2. **Проверьте статус webhook:**
   ```bash
   curl https://ваш-проект.vercel.app/api/webhook/status
   ```

### Шаг 4: Проверьте бота в Telegram

1. **Найдите вашего бота в Telegram**
2. **Отправьте команду:** `/start`
3. **Проверьте, что бот не заблокирован**

### Шаг 5: Проверьте логи

1. **В Vercel Dashboard → Functions → api/webhook**
2. **Проверьте логи на ошибки**

## 🚨 Частые проблемы и решения

### Проблема 1: "Bot token not configured"

**Решение:**
1. Добавьте `TELEGRAM_BOT_TOKEN` в переменные окружения
2. Перезапустите деплой

### Проблема 2: "Webhook not set"

**Решение:**
```bash
curl https://ваш-проект.vercel.app/api/webhook/setup
```

### Проблема 3: "Bot not responding"

**Возможные причины:**
1. Бот заблокирован
2. Неправильный токен
3. Webhook не настроен

**Решение:**
1. Проверьте токен в @BotFather
2. Настройте webhook заново
3. Перезапустите деплой

### Проблема 4: "Function timeout"

**Решение:**
1. Увеличьте timeout в vercel.json
2. Оптимизируйте код

## 🧪 Тестовые команды

### Проверка конфигурации:
```bash
curl https://ваш-проект.vercel.app/api/test-bot
```

### Проверка webhook:
```bash
curl https://ваш-проект.vercel.app/api/webhook/status
```

### Настройка webhook:
```bash
curl https://ваш-проект.vercel.app/api/webhook/setup
```

### Проверка основного приложения:
```bash
curl https://ваш-проект.vercel.app/api/bot/status
```

## 📋 Чек-лист диагностики

- [ ] Проект задеплоен с последними изменениями
- [ ] Переменные окружения настроены
- [ ] Webhook настроен
- [ ] Бот не заблокирован
- [ ] Токен правильный
- [ ] Логи не содержат ошибок

## 🆘 Если ничего не помогает

1. **Пересоздайте бота** в @BotFather
2. **Получите новый токен**
3. **Обновите переменные окружения**
4. **Перезапустите деплой**
5. **Настройте webhook заново**

---

**Полезные ссылки:**
- [Vercel Function Logs](https://vercel.com/docs/concepts/functions/function-logs)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables) 