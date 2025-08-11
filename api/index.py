from flask import Flask, jsonify, request
import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Конфигурация
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://telegram-games-two.vercel.app')

# Создаем приложение бота
if BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE':
    application = Application.builder().token(BOT_TOKEN).build()
    
    def setup_handlers():
        """Настройка обработчиков команд"""
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("games", games_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CallbackQueryHandler(button_callback))
    
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        welcome_text = f"""
🎮 Добро пожаловать в Игровой Бот!

Привет, {user.first_name}! 👋

Я предлагаю вам сыграть в классические настольные игры:
♔ Шахматы - стратегия и тактика
⚪ Шашки - быстрая и динамичная игра

Используйте команды:
/games - Выбрать игру
/help - Справка

Или нажмите кнопку ниже, чтобы начать играть прямо сейчас!
        """
        
        keyboard = [
            [InlineKeyboardButton("🎮 Играть в игры", web_app=WebAppInfo(url=f"{WEBAPP_URL}"))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
    async def games_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /games"""
        games_text = """
🎯 Выберите игру:

♔ <b>Шахматы</b>
   • Классическая игра стратегии
   • Полная логика всех фигур
   • Шах и мат
   • Рокировка и специальные ходы

⚪ <b>Шашки</b>
   • Быстрая и динамичная игра
   • Обязательные взятия
   • Дамки
   • Множественные взятия

Нажмите кнопку ниже, чтобы открыть игровую платформу!
        """
        
        keyboard = [
            [InlineKeyboardButton("♔ Шахматы", web_app=WebAppInfo(url=f"{WEBAPP_URL}?game=chess"))],
            [InlineKeyboardButton("⚪ Шашки", web_app=WebAppInfo(url=f"{WEBAPP_URL}?game=checkers"))],
            [InlineKeyboardButton("🎮 Все игры", web_app=WebAppInfo(url=f"{WEBAPP_URL}"))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            games_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
🤖 <b>Справка по боту</b>

<b>Доступные команды:</b>
/start - Начать работу с ботом
/games - Выбрать игру
/help - Показать эту справку

<b>Как играть:</b>
1. Нажмите кнопку "🎮 Играть в игры"
2. Выберите игру (шахматы или шашки)
3. Играйте в браузере Telegram

<b>Поддержка:</b>
Если у вас есть вопросы, обратитесь к разработчику.
        """
        
        await update.message.reply_text(help_text, parse_mode='HTML')
        
    async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        # Здесь можно добавить дополнительную логику для кнопок
        await query.edit_message_text("🎮 Открываю игровую платформу...")

    # Настраиваем обработчики
    setup_handlers()
else:
    application = None
    logger.warning("Bot token not configured!")

@app.route('/', methods=['GET'])
def index():
    """Главная страница API"""
    return jsonify({
        'message': 'Telegram Games API is running on Vercel!',
        'status': 'ok',
        'platform': 'vercel',
        'bot_configured': bool(BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE'),
        'webapp_url': WEBAPP_URL
    })

@app.route('/api', methods=['GET'])
def api_root():
    """API root endpoint"""
    return jsonify({
        'message': 'Telegram Games API is running on Vercel!',
        'status': 'ok',
        'platform': 'vercel',
        'endpoints': [
            '/api/status',
            '/api/health',
            '/api/test',
            '/api/test-bot',
            '/api/webhook',
            '/api/webhook/setup',
            '/api/webhook/status',
            '/api/test-message'
        ]
    })

@app.route('/api/status', methods=['GET'])
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'running',
        'environment': os.getenv('VERCEL_ENV', 'development'),
        'region': os.getenv('VERCEL_REGION', 'unknown'),
        'platform': 'vercel',
        'version': '1.0.0',
        'bot_configured': bool(BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE')
    })

@app.route('/api/health', methods=['GET'])
def api_health():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'message': 'API is running on Vercel',
        'platform': 'vercel'
    }), 200

@app.route('/api/test', methods=['GET'])
def api_test():
    """API test endpoint"""
    return jsonify({
        'message': 'API test endpoint working on Vercel!',
        'status': 'ok',
        'platform': 'vercel'
    }), 200

@app.route('/api/test-bot', methods=['GET'])
def test_bot():
    """Тестовый endpoint для проверки бота"""
    return jsonify({
        'message': 'Bot Test Endpoint',
        'status': 'running',
        'bot_token_configured': bool(BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE'),
        'bot_token_length': len(BOT_TOKEN) if BOT_TOKEN else 0,
        'webapp_url': WEBAPP_URL,
        'environment_variables': {
            'TELEGRAM_BOT_TOKEN': '***' if BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE' else 'NOT_SET',
            'WEBAPP_URL': WEBAPP_URL
        }
    })

@app.route('/api/test-message', methods=['POST'])
def test_message():
    """Тестовый endpoint для проверки получения сообщений"""
    try:
        data = request.get_json()
        logger.info(f"Received test message: {data}")
        return jsonify({
            'status': 'ok',
            'message': 'Test message received',
            'data': data
        }), 200
    except Exception as e:
        logger.error(f"Error processing test message: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhook', methods=['GET', 'POST'])
def webhook():
    """Webhook endpoint для Telegram бота"""
    if request.method == 'GET':
        # Информация о webhook
        webhook_url = f"{WEBAPP_URL}/api/webhook"
        return jsonify({
            'webhook_url': webhook_url,
            'webhook_setup_url': f"{WEBAPP_URL}/api/webhook/setup",
            'webhook_status_url': f"{WEBAPP_URL}/api/webhook/status",
            'bot_configured': bool(application)
        })
    
    elif request.method == 'POST':
        # Обработка webhook от Telegram
        if not application:
            return jsonify({'error': 'Bot not configured'}), 400
        
        try:
            # Логируем входящие данные
            data = request.get_json()
            logger.info(f"Received webhook data: {data}")
            
            # Получаем данные от Telegram
            update = Update.de_json(data, application.bot)
            
            # Создаем новую event loop для асинхронной операции
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Обрабатываем обновление асинхронно
            loop.run_until_complete(application.process_update(update))
            
            return jsonify({'status': 'ok'}), 200
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/webhook/setup', methods=['GET'])
def setup_webhook():
    """Настройка webhook для бота"""
    if not application:
        return jsonify({'error': 'Bot not configured'}), 400
    
    try:
        # Получаем URL для webhook
        webhook_url = f"{WEBAPP_URL}/api/webhook"
        
        # Создаем новую event loop для асинхронной операции
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Устанавливаем webhook
        result = loop.run_until_complete(application.bot.set_webhook(url=webhook_url))
        
        return jsonify({
            'status': 'ok',
            'webhook_url': webhook_url,
            'result': result
        }), 200
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhook/status', methods=['GET'])
def webhook_status():
    """Статус webhook"""
    if not application:
        return jsonify({'error': 'Bot not configured'}), 400
    
    try:
        # Создаем новую event loop для асинхронной операции
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        webhook_info = loop.run_until_complete(application.bot.get_webhook_info())
        return jsonify({
            'status': 'ok',
            'webhook_info': webhook_info.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        return jsonify({'error': str(e)}), 500

# Export the Flask app for Vercel
app.debug = False 