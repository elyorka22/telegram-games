from flask import Flask, request, jsonify
import os
import logging
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

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
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://your-app-name.vercel.app')

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

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint для Telegram бота"""
    if not application:
        return jsonify({'error': 'Bot not configured'}), 400
    
    try:
        # Получаем данные от Telegram
        update = Update.de_json(request.get_json(), application.bot)
        
        # Обрабатываем обновление
        application.process_update(update)
        
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/setup', methods=['GET'])
def setup_webhook():
    """Настройка webhook для бота"""
    if not application:
        return jsonify({'error': 'Bot not configured'}), 400
    
    try:
        # Получаем URL для webhook
        webhook_url = f"{WEBAPP_URL}/api/webhook"
        
        # Устанавливаем webhook
        result = application.bot.set_webhook(url=webhook_url)
        
        return jsonify({
            'status': 'ok',
            'webhook_url': webhook_url,
            'result': result
        }), 200
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/status', methods=['GET'])
def webhook_status():
    """Статус webhook"""
    if not application:
        return jsonify({'error': 'Bot not configured'}), 400
    
    try:
        webhook_info = application.bot.get_webhook_info()
        return jsonify({
            'status': 'ok',
            'webhook_info': webhook_info.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """Главная страница API"""
    return jsonify({
        'message': 'Telegram Bot Webhook API',
        'status': 'running',
        'bot_configured': bool(application),
        'webhook_url': f"{WEBAPP_URL}/api/webhook" if application else None
    })

# Export the Flask app for Vercel
app.debug = False 