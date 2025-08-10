import os
import logging
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, render_template
import threading
import time
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация для Railway
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'http://localhost:5000')
PORT = int(os.getenv('PORT', 5000))
HOST = os.getenv('HOST', '0.0.0.0')

class TelegramGameBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
        
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("games", self.games_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
    async def games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📖 <b>Справка по играм</b>

<b>♔ Шахматы:</b>
• Цель: поставить мат королю противника
• Пешка: ходит на 1 клетку вперед, бьет по диагонали
• Ладья: ходит по горизонтали и вертикали
• Конь: ходит буквой "Г"
• Слон: ходит по диагонали
• Ферзь: ходит как ладья + слон
• Король: ходит на 1 клетку в любом направлении

<b>⚪ Шашки:</b>
• Цель: захватить все шашки противника
• Обычная шашка: ходит только вперед по диагонали
• Взятие: обязательно, если возможно
• Дамка: при достижении последней горизонтали
• Дамка: ходит по диагонали на любое расстояние

<b>Команды бота:</b>
/start - Главное меню
/games - Выбор игры
/help - Эта справка

<b>Как играть:</b>
1. Нажмите кнопку "Играть в игры"
2. Выберите тип игры (шахматы или шашки)
3. Дождитесь подключения противника
4. Играйте в реальном времени!

Удачной игры! 🎮
        """
        
        keyboard = [
            [InlineKeyboardButton("🎮 Начать игру", web_app=WebAppInfo(url=f"{WEBAPP_URL}"))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        # Обработка данных от Mini App
        if query.data and query.data.startswith('web_app_data'):
            # Здесь можно обработать данные, отправленные из Mini App
            await query.edit_message_text("Данные получены от игры!")
            
    def run(self):
        """Запуск бота"""
        logger.info("Запуск Telegram бота...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def run_flask_app():
    """Запуск Flask приложения в отдельном потоке"""
    from app import app, socketio
    socketio.run(app, debug=False, host=HOST, port=PORT, allow_unsafe_werkzeug=True)

def main():
    """Главная функция"""
    logger.info(f"Запуск приложения на {HOST}:{PORT}")
    logger.info(f"WebApp URL: {WEBAPP_URL}")
    
    # Запускаем Flask приложение в отдельном потоке
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    
    # Даем время Flask приложению запуститься
    time.sleep(3)
    
    # Запускаем Telegram бота
    bot = TelegramGameBot()
    bot.run()

if __name__ == '__main__':
    main() 