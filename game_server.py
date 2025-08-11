from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
from chess_game import ChessGame
from checkers_game import CheckersGame
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Хранилище активных игр
active_games = {}

@app.route('/')
def index():
    return "Game Server is running"

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_game')
def handle_join_game(data):
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    
    if not game_id:
        emit('error', {'message': 'Game ID required'})
        return
    
    # Присоединяемся к комнате игры
    join_room(game_id)
    
    # Если игра не существует, создаем её
    if game_id not in active_games:
        # Получаем информацию об игре из API лобби
        # Пока создаем тестовую игру
        game_type = data.get('game_type', 'chess')
        if game_type == 'chess':
            game = ChessGame('player1', 'player2')
        else:
            game = CheckersGame('player1', 'player2')
        
        active_games[game_id] = {
            'game': game,
            'players': {},
            'type': game_type
        }
    
    game_info = active_games[game_id]
    
    # Определяем цвет игрока
    if len(game_info['players']) == 0:
        color = 'white'
    elif len(game_info['players']) == 1:
        color = 'black'
    else:
        emit('error', {'message': 'Game is full'})
        return
    
    # Добавляем игрока
    game_info['players'][player_id] = {
        'color': color,
        'ready': True
    }
    
    # Отправляем информацию об игре
    emit('game_joined', {
        'game_id': game_id,
        'color': color,
        'game_type': game_info['type'],
        'board': game_info['game'].board,
        'status': game_info['game'].get_game_status()
    })
    
    # Уведомляем других игроков
    emit('player_joined', {
        'player_id': player_id,
        'color': color
    }, room=game_id, include_self=False)

@socketio.on('make_move')
def handle_make_move(data):
    game_id = data.get('game_id')
    from_pos = data.get('from_pos')
    to_pos = data.get('to_pos')
    player_id = data.get('player_id')
    
    if game_id not in active_games:
        emit('error', {'message': 'Game not found'})
        return
    
    game_info = active_games[game_id]
    game = game_info['game']
    
    # Проверяем, чей ход
    current_turn = 'white' if game.current_turn.value == 'white' else 'black'
    player_color = game_info['players'].get(player_id, {}).get('color')
    
    if player_color != current_turn:
        emit('error', {'message': 'Not your turn'})
        return
    
    # Делаем ход
    success = game.make_move(from_pos, to_pos)
    
    if success:
        # Обновляем статус игры
        game.check_game_state()
        
        # Отправляем обновление всем игрокам
        emit('move_made', {
            'from_pos': from_pos,
            'to_pos': to_pos,
            'board': game.board,
            'status': game.get_game_status(),
            'game_over': game.game_over,
            'winner': game.winner.value if game.winner else None
        }, room=game_id)
    else:
        emit('error', {'message': 'Invalid move'})

@socketio.on('get_valid_moves')
def handle_get_valid_moves(data):
    game_id = data.get('game_id')
    position = data.get('position')
    player_id = data.get('player_id')
    
    if game_id not in active_games:
        emit('error', {'message': 'Game not found'})
        return
    
    game_info = active_games[game_id]
    game = game_info['game']
    
    valid_moves = game.get_valid_moves(position)
    emit('valid_moves', {'moves': valid_moves})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5002) 