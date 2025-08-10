from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from chess_game import ChessGame, Color
from checkers_game import CheckersGame, CheckerColor
import uuid
import json
import os
import threading
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'chess_secret_key_2024')
socketio = SocketIO(app, cors_allowed_origins="*")

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

@socketio.on('connect')
def handle_connect():
    """Обработчик подключения клиента"""
    print(f'Клиент подключился: {request.sid}')
    emit('connected', {'sid': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    """Обработчик отключения клиента"""
    print(f'Клиент отключился: {request.sid}')
    # Удаляем игрока из очереди ожидания
    for game_type in waiting_players:
        if request.sid in waiting_players[game_type]:
            waiting_players[game_type].remove(request.sid)
    
    # Удаляем игрока из игры
    for game_id, game_data in active_games.items():
        if request.sid in [game_data['white_player'], game_data['black_player']]:
            # Уведомляем другого игрока
            other_player = game_data['black_player'] if request.sid == game_data['white_player'] else game_data['white_player']
            emit('opponent_disconnected', room=other_player)
            # Удаляем игру
            del active_games[game_id]
            break

@socketio.on('find_game')
def handle_find_game(data):
    """Поиск игры или создание новой"""
    player_id = request.sid
    game_type = data.get('game_type', 'chess')  # По умолчанию шахматы
    
    if game_type not in ['chess', 'checkers']:
        emit('error', {'message': 'Неизвестный тип игры'})
        return
    
    if player_id in waiting_players[game_type]:
        emit('error', {'message': 'Вы уже в очереди ожидания'})
        return
    
    if waiting_players[game_type]:
        # Есть ожидающий игрок - создаем игру
        opponent_id = waiting_players[game_type].pop(0)
        game_id = str(uuid.uuid4())
        
        # Создаем новую игру в зависимости от типа
        if game_type == 'chess':
            game = ChessGame(opponent_id, player_id)
        else:  # checkers
            game = CheckersGame(opponent_id, player_id)
        
        active_games[game_id] = {
            'game': game,
            'white_player': opponent_id,
            'black_player': player_id,
            'game_type': game_type
        }
        
        # Подключаем игроков к комнате игры
        join_room(game_id)
        
        # Уведомляем игроков о начале игры
        emit('game_started', {
            'game_id': game_id,
            'color': 'white',
            'board': get_board_state(game, game_type),
            'game_type': game_type
        }, room=opponent_id)
        
        emit('game_started', {
            'game_id': game_id,
            'color': 'black',
            'board': get_board_state(game, game_type),
            'game_type': game_type
        }, room=player_id)
        
    else:
        # Нет ожидающих игроков - добавляем в очередь
        waiting_players[game_type].append(player_id)
        game_name = "шахматы" if game_type == 'chess' else "шашки"
        emit('waiting_for_opponent', {'message': f'Ожидание противника для игры в {game_name}...'})

@socketio.on('join_game')
def handle_join_game(data):
    """Присоединение к существующей игре"""
    game_id = data.get('game_id')
    player_id = request.sid
    
    if game_id not in active_games:
        emit('error', {'message': 'Игра не найдена'})
        return
    
    game_data = active_games[game_id]
    game = game_data['game']
    game_type = game_data['game_type']
    
    # Определяем цвет игрока
    if game_data['white_player'] == player_id:
        color = 'white'
    elif game_data['black_player'] == player_id:
        color = 'black'
    else:
        emit('error', {'message': 'Вы не являетесь участником этой игры'})
        return
    
    join_room(game_id)
    emit('game_joined', {
        'game_id': game_id,
        'color': color,
        'board': get_board_state(game, game_type),
        'status': game.get_game_status(),
        'game_type': game_type
    })

@socketio.on('make_move')
def handle_make_move(data):
    """Обработка хода"""
    game_id = data.get('game_id')
    from_pos = tuple(data.get('from_pos'))
    to_pos = tuple(data.get('to_pos'))
    player_id = request.sid
    
    if game_id not in active_games:
        emit('error', {'message': 'Игра не найдена'})
        return
    
    game_data = active_games[game_id]
    game = game_data['game']
    game_type = game_data['game_type']
    
    # Проверяем, что ходит правильный игрок
    if game_type == 'chess':
        current_color = game.current_turn
        if (current_color == Color.WHITE and game_data['white_player'] != player_id) or \
           (current_color == Color.BLACK and game_data['black_player'] != player_id):
            emit('error', {'message': 'Не ваш ход'})
            return
    else:  # checkers
        current_color = game.current_turn
        if (current_color == CheckerColor.WHITE and game_data['white_player'] != player_id) or \
           (current_color == CheckerColor.BLACK and game_data['black_player'] != player_id):
            emit('error', {'message': 'Не ваш ход'})
            return
    
    # Выполняем ход
    if game.make_move(from_pos, to_pos):
        # Уведомляем всех игроков в комнате об обновлении
        winner = None
        if game_type == 'chess':
            winner = game.winner.value if game.winner else None
        else:  # checkers
            winner = game.winner.value if game.winner else None
        
        emit('move_made', {
            'from_pos': from_pos,
            'to_pos': to_pos,
            'board': get_board_state(game, game_type),
            'status': game.get_game_status(),
            'game_over': game.game_over,
            'winner': winner
        }, room=game_id)
        
        # Если игра окончена, удаляем её
        if game.game_over:
            del active_games[game_id]
    else:
        emit('error', {'message': 'Недопустимый ход'})

@socketio.on('get_valid_moves')
def handle_get_valid_moves(data):
    """Получение допустимых ходов для фигуры"""
    game_id = data.get('game_id')
    position = tuple(data.get('position'))
    player_id = request.sid
    
    if game_id not in active_games:
        emit('error', {'message': 'Игра не найдена'})
        return
    
    game_data = active_games[game_id]
    game = game_data['game']
    
    valid_moves = game.get_valid_moves(position)
    emit('valid_moves', {'moves': valid_moves})

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

def start_telegram_bot():
    """Запуск Telegram бота в отдельном потоке"""
    try:
        from telegram_bot import TelegramGameBot
        bot = TelegramGameBot()
        bot.run()
    except Exception as e:
        logger.error(f"Ошибка запуска Telegram бота: {e}")

# Запускаем Telegram бота в отдельном потоке при импорте
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
if bot_token and bot_token != 'YOUR_BOT_TOKEN_HERE':
    bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
    bot_thread.start()
    logger.info("Telegram бот запущен в отдельном потоке")
else:
    logger.warning("TELEGRAM_BOT_TOKEN не установлен, бот не запущен")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Запуск приложения на {host}:{port}")
    socketio.run(app, debug=debug, host=host, port=port, allow_unsafe_werkzeug=True) 