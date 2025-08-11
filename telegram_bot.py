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
        self.application.add_handler(CommandHandler("join", self.join_game_command))
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

Выберите тип игры или нажмите кнопку для открытия игровой платформы!
        """
        
        keyboard = [
            [InlineKeyboardButton("♔ Создать шахматы", callback_data="create_chess")],
            [InlineKeyboardButton("⚪ Создать шашки", callback_data="create_checkers")],
            [InlineKeyboardButton("🎮 Открыть платформу", web_app=WebAppInfo(url=f"{WEBAPP_URL}"))]
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
        
        # Обработка создания игр
        if query.data == "create_chess":
            await self.create_game_direct(update, context, "chess")
        elif query.data == "create_checkers":
            await self.create_game_direct(update, context, "checkers")
        # Обработка данных от Mini App
        elif query.data and query.data.startswith('web_app_data'):
            # Здесь можно обработать данные, отправленные из Mini App
            await query.edit_message_text("Данные получены от игры!")
    
    async def create_game_direct(self, update: Update, context: ContextTypes.DEFAULT_TYPE, game_type: str):
        """Создание игры прямо в боте"""
        user = update.effective_user
        
        try:
            # Создаем игру через API
            import requests
            import json
            
            game_data = {
                'user_id': str(user.id),
                'username': user.username or user.first_name or 'Player',
                'game_type': game_type
            }
            
            response = requests.post(
                f"{WEBAPP_URL}/api/lobby/create",
                headers={'Content-Type': 'application/json'},
                json=game_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'ok':
                    game_id = data['game']['id']
                    game_name = "шахматы" if game_type == "chess" else "шашки"
                    
                    # Создаем кнопку для присоединения к игре
                    keyboard = [
                        [InlineKeyboardButton("🎮 Присоединиться к игре", web_app=WebAppInfo(url=f"{WEBAPP_URL}/game?game_id={game_id}&type={game_type}"))],
                        [InlineKeyboardButton("📋 Поделиться ссылкой", callback_data=f"share_game_{game_id}")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.edit_message_text(
                        f"✅ Игра в {game_name} создана!\n\n"
                        f"🆔 ID игры: <code>{game_id}</code>\n"
                        f"👤 Создатель: {user.first_name}\n"
                        f"⏳ Статус: Ожидание игрока\n\n"
                        f"Отправьте ID игры другу или нажмите кнопку для присоединения!",
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
                else:
                    await query.edit_message_text(f"❌ Ошибка создания игры: {data.get('error', 'Неизвестная ошибка')}")
            else:
                await query.edit_message_text("❌ Ошибка подключения к серверу")
                
        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка: {str(e)}")
    
    async def join_game_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Присоединение к игре по ID"""
        user = update.effective_user
        
        # Проверяем, есть ли ID игры в команде
        if not context.args:
            await update.message.reply_text(
                "🎮 <b>Присоединение к игре</b>\n\n"
                "Использование: <code>/join GAME_ID</code>\n\n"
                "Пример: <code>/join abc12345</code>\n\n"
                "Получите ID игры от друга, который создал игру!",
                parse_mode='HTML'
            )
            return
        
        game_id = context.args[0]
        
        try:
            # Присоединяемся к игре через API
            import requests
            
            join_data = {
                'user_id': str(user.id),
                'username': user.username or user.first_name or 'Player',
                'game_id': game_id
            }
            
            response = requests.post(
                f"{WEBAPP_URL}/api/lobby/join",
                headers={'Content-Type': 'application/json'},
                json=join_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'ok':
                    game_type = data['game']['type']
                    game_name = "шахматы" if game_type == "chess" else "шашки"
                    
                    if data['game']['status'] == 'playing':
                        # Игра готова к началу
                        keyboard = [
                            [InlineKeyboardButton("🎮 Начать игру!", web_app=WebAppInfo(url=f"{WEBAPP_URL}/game?game_id={game_id}&type={game_type}"))]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        await update.message.reply_text(
                            f"🎉 <b>Игра начинается!</b>\n\n"
                            f"🎮 Тип: {game_name}\n"
                            f"🆔 ID: <code>{game_id}</code>\n"
                            f"👥 Игроков: {len(data['game']['players'])}/2\n\n"
                            f"Нажмите кнопку, чтобы начать играть!",
                            reply_markup=reply_markup,
                            parse_mode='HTML'
                        )
                    else:
                        # Ожидание второго игрока
                        await update.message.reply_text(
                            f"✅ <b>Присоединились к игре!</b>\n\n"
                            f"🎮 Тип: {game_name}\n"
                            f"🆔 ID: <code>{game_id}</code>\n"
                            f"👥 Игроков: {len(data['game']['players'])}/2\n"
                            f"⏳ Статус: Ожидание второго игрока\n\n"
                            f"Вы будете уведомлены, когда игра начнется!",
                            parse_mode='HTML'
                        )
                else:
                    await update.message.reply_text(f"❌ Ошибка: {data.get('error', 'Неизвестная ошибка')}")
            else:
                await update.message.reply_text("❌ Ошибка подключения к серверу")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
        
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