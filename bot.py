import logging
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN, BOT_NAME
from game_logic import QuizGame

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Создаем экземпляр игры
quiz_game = QuizGame()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    welcome_text = f"""
🎮 Привет, {user.first_name}! 

Я {BOT_NAME} - бот для игры в викторину!

📚 У меня есть интересные вопросы на разные темы.
🎯 Отвечайте правильно и набирайте очки!
🏆 Соревнуйтесь с друзьями!

Команды:
/start - Начать новую игру
/stats - Ваша статистика
/leaderboard - Таблица лидеров
/help - Помощь

Нажмите кнопку ниже, чтобы начать игру!
    """.strip()
    
    # Создаем кнопку для начала игры
    from telegram import InlineKeyboardButton
    keyboard = [[InlineKeyboardButton("🎮 Начать игру", callback_data="start_game")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
📖 Помощь по игре

🎮 Как играть:
1. Нажмите "Начать игру" или используйте /start
2. Отвечайте на вопросы, выбирая один из вариантов
3. За каждый правильный ответ получаете 1 очко
4. В конце игры увидите свой результат

📊 Статистика:
• Ваш общий счет сохраняется между играми
• Используйте /stats для просмотра ваших результатов
• Используйте /leaderboard для просмотра лучших игроков

🎯 Советы:
• Внимательно читайте вопросы
• Не торопитесь с ответами
• Изучайте объяснения к неправильным ответам

Удачи в игре! 🍀
    """.strip()
    
    await update.message.reply_text(help_text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stats"""
    user_id = update.effective_user.id
    stats = quiz_game.get_user_stats(user_id)
    
    stats_text = f"""
📊 Ваша статистика

👤 Пользователь: {update.effective_user.first_name}
🎯 Общий счет: {stats['total_score']} очков
🎮 Игр сыграно: {stats['games_played']}
🎲 Текущая игра: {'Да' if stats['current_game'] else 'Нет'}

🏆 Ваша позиция в рейтинге: {quiz_game.get_leaderboard().index((user_id, stats['total_score'])) + 1 if (user_id, stats['total_score']) in quiz_game.get_leaderboard() else 'Не в топе'}
    """.strip()
    
    await update.message.reply_text(stats_text)

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /leaderboard"""
    leaderboard = quiz_game.get_leaderboard()
    
    if not leaderboard:
        await update.message.reply_text("📊 Пока нет данных для таблицы лидеров. Сыграйте в игру!")
        return
    
    leaderboard_text = "🏆 Таблица лидеров\n\n"
    
    for i, (user_id, score) in enumerate(leaderboard, 1):
        # Получаем информацию о пользователе
        try:
            user = await context.bot.get_chat(user_id)
            username = user.first_name or f"Пользователь {user_id}"
        except:
            username = f"Пользователь {user_id}"
        
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        leaderboard_text += f"{medal} {username}: {score} очков\n"
    
    await update.message.reply_text(leaderboard_text)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()  # Убираем "часики" у кнопки
    
    user_id = query.from_user.id
    
    if query.data == "start_game":
        # Начинаем новую игру
        text, keyboard = quiz_game.start_game(user_id)
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    elif query.data.startswith("answer_"):
        # Обрабатываем ответ
        answer_index = int(query.data.split("_")[1])
        text, keyboard, is_finished = quiz_game.process_answer(user_id, answer_index)
        
        if is_finished:
            # Игра окончена, убираем клавиатуру
            await query.edit_message_text(text=text)
        else:
            # Показываем следующий вопрос
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=text, reply_markup=reply_markup)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Отправляем сообщение пользователю об ошибке
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "😔 Произошла ошибка. Попробуйте еще раз или используйте /start для перезапуска."
        )

def main():
    """Основная функция запуска бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("leaderboard", leaderboard_command))
    
    # Добавляем обработчик нажатий на кнопки
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info(f"Бот {BOT_NAME} запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 