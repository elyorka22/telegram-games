from flask import Flask, render_template, request, jsonify
import os
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'chess_secret_key_2024')

# Временно отключаем WebSocket для упрощения запуска
# socketio = SocketIO(app, cors_allowed_origins="*")

# Хранилище активных игр
active_games = {}
waiting_players = {
    'chess': [],
    'checkers': []
}

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint для Railway"""
    return jsonify({
        'status': 'healthy',
        'message': 'Application is running',
        'active_games': len(active_games),
        'waiting_players': {
            'chess': len(waiting_players['chess']),
            'checkers': len(waiting_players['checkers'])
        }
    }), 200

@app.route('/game/<game_id>')
def game_room(game_id):
    """Страница игры"""
    if game_id not in active_games:
        return "Игра не найдена", 404
    return render_template('game.html', game_id=game_id)

@app.route('/test')
def test():
    """Тестовый endpoint"""
    return jsonify({
        'message': 'Application is working!',
        'status': 'ok'
    }), 200

# Временно отключаем WebSocket обработчики
# @socketio.on('connect')
# def handle_connect():
#     """Обработчик подключения клиента"""
#     print(f'Клиент подключился: {request.sid}')
#     emit('connected', {'sid': request.sid})

# @socketio.on('disconnect')
# def handle_disconnect():
#     """Обработчик отключения клиента"""
#     print(f'Клиент отключился: {request.sid}')
#     # Удаляем игрока из очереди ожидания
#     for game_type in waiting_players:
#         if request.sid in waiting_players[game_type]:
#             waiting_players[game_type].remove(request.sid)
    
#     # Удаляем игрока из игры
#     for game_id, game_data in active_games.items():
#         if request.sid in [game_data['white_player'], game_data['black_player']]:
#             # Уведомляем другого игрока
#             other_player = game_data['black_player'] if request.sid == game_data['white_player'] else game_data['white_player']
#             emit('opponent_disconnected', room=other_player)
#             # Удаляем игру
#             del active_games[game_id]
#             break

# Временно отключаем остальные WebSocket обработчики
# @socketio.on('find_game')
# def handle_find_game(data):
#     pass

# @socketio.on('join_game')
# def handle_join_game(data):
#     pass

# @socketio.on('make_move')
# def handle_make_move(data):
#     pass

# @socketio.on('get_valid_moves')
# def handle_get_valid_moves(data):
#     pass

def get_board_state(game, game_type):
    """Преобразует состояние доски в JSON"""
    board_state = []
    for row in range(8):
        board_row = []
        for col in range(8):
            piece = game.board[row][col]
            if piece:
                if game_type == 'chess':
                    board_row.append({
                        'type': piece.type.value,
                        'color': piece.color.value,
                        'symbol': piece.get_symbol()
                    })
                else:  # checkers
                    board_row.append({
                        'type': piece.type.value,
                        'color': piece.color.value,
                        'symbol': piece.get_symbol(),
                        'is_king': piece.is_king
                    })
            else:
                board_row.append(None)
        board_state.append(board_row)
    return board_state

# Временно отключаем Telegram бота
# def start_telegram_bot():
#     """Запуск Telegram бота в отдельном потоке"""
#     try:
#         from telegram_bot import TelegramGameBot
#         bot = TelegramGameBot()
#         bot.run()
#     except Exception as e:
#         logger.error(f"Ошибка запуска Telegram бота: {e}")

# # Запускаем Telegram бота в отдельном потоке при импорте
# bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
# if bot_token and bot_token != 'YOUR_BOT_TOKEN_HERE':
#     bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
#     bot_thread.start()
#     logger.info("Telegram бот запущен в отдельном потоке")
# else:
#     logger.warning("TELEGRAM_BOT_TOKEN не установлен, бот не запущен")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Запуск приложения на {host}:{port}")
    app.run(debug=debug, host=host, port=port) 