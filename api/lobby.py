from flask import Flask, jsonify, request
import os
import json
import time
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)

# Добавляем CORS заголовки
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Хранилище лобби (в реальном проекте это должна быть база данных)
LOBBY_STORAGE = {
    'games': {},  # {game_id: game_info}
    'users': {}   # {user_id: user_info}
}

class LobbyManager:
    def __init__(self):
        self.games = LOBBY_STORAGE['games']
        self.users = LOBBY_STORAGE['users']
    
    def create_game(self, user_id, username, game_type):
        """Создать новую игру"""
        game_id = str(uuid.uuid4())[:8]
        game_info = {
            'id': game_id,
            'type': game_type,
            'creator': {
                'id': user_id,
                'username': username
            },
            'players': [{
                'id': user_id,
                'username': username,
                'ready': True
            }],
            'status': 'waiting',  # waiting, playing, finished
            'created_at': datetime.now().isoformat(),
            'max_players': 2
        }
        
        self.games[game_id] = game_info
        self.users[user_id] = {
            'current_game': game_id,
            'username': username
        }
        
        return game_info
    
    def join_game(self, user_id, username, game_id):
        """Присоединиться к игре"""
        if game_id not in self.games:
            return None, "Игра не найдена"
        
        game = self.games[game_id]
        
        if game['status'] != 'waiting':
            return None, "Игра уже началась"
        
        if len(game['players']) >= game['max_players']:
            return None, "Игра заполнена"
        
        # Проверяем, не в игре ли уже пользователь
        for player in game['players']:
            if player['id'] == user_id:
                return game, "Вы уже в этой игре"
        
        # Добавляем игрока
        game['players'].append({
            'id': user_id,
            'username': username,
            'ready': True
        })
        
        # Обновляем информацию о пользователе
        self.users[user_id] = {
            'current_game': game_id,
            'username': username
        }
        
        # Если игра заполнена, начинаем
        if len(game['players']) == game['max_players']:
            game['status'] = 'playing'
            game['started_at'] = datetime.now().isoformat()
        
        return game, "Успешно присоединились"
    
    def get_available_games(self):
        """Получить список доступных игр"""
        available = []
        for game_id, game in self.games.items():
            if game['status'] == 'waiting' and len(game['players']) < game['max_players']:
                available.append({
                    'id': game_id,
                    'type': game['type'],
                    'creator': game['creator']['username'],
                    'players_count': len(game['players']),
                    'max_players': game['max_players'],
                    'created_at': game['created_at']
                })
        return available
    
    def get_game_info(self, game_id):
        """Получить информацию об игре"""
        return self.games.get(game_id)
    
    def leave_game(self, user_id, game_id):
        """Покинуть игру"""
        if game_id not in self.games:
            return False, "Игра не найдена"
        
        game = self.games[game_id]
        
        # Удаляем игрока из игры
        game['players'] = [p for p in game['players'] if p['id'] != user_id]
        
        # Если игра пустая, удаляем её
        if len(game['players']) == 0:
            del self.games[game_id]
        else:
            # Если игра была в процессе, возвращаем в ожидание
            if game['status'] == 'playing':
                game['status'] = 'waiting'
        
        # Удаляем пользователя из хранилища
        if user_id in self.users:
            del self.users[user_id]
        
        return True, "Успешно покинули игру"
    
    def cleanup_old_games(self):
        """Очистка старых игр"""
        current_time = datetime.now()
        games_to_remove = []
        
        for game_id, game in self.games.items():
            created_time = datetime.fromisoformat(game['created_at'])
            if (current_time - created_time).seconds > 3600:  # 1 час
                games_to_remove.append(game_id)
        
        for game_id in games_to_remove:
            del self.games[game_id]

# Создаем менеджер лобби
lobby_manager = LobbyManager()

@app.route('/')
def index():
    """Главная страница API лобби"""
    return jsonify({
        'message': 'Lobby API is running',
        'status': 'ok',
        'endpoints': [
            '/api/lobby/games',
            '/api/lobby/create',
            '/api/lobby/join',
            '/api/lobby/game/<game_id>',
            '/api/lobby/leave'
        ]
    })

@app.route('/api/lobby/games', methods=['GET'])
def get_games():
    """Получить список доступных игр"""
    try:
        # Очищаем старые игры
        lobby_manager.cleanup_old_games()
        
        games = lobby_manager.get_available_games()
        return jsonify({
            'status': 'ok',
            'games': games,
            'count': len(games)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lobby/create', methods=['POST'])
def create_game():
    """Создать новую игру"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        username = data.get('username')
        game_type = data.get('game_type', 'chess')
        
        if not user_id or not username:
            return jsonify({'error': 'user_id и username обязательны'}), 400
        
        game_info = lobby_manager.create_game(user_id, username, game_type)
        
        return jsonify({
            'status': 'ok',
            'message': 'Игра создана',
            'game': game_info
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lobby/join', methods=['POST'])
def join_game():
    """Присоединиться к игре"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        username = data.get('username')
        game_id = data.get('game_id')
        
        if not user_id or not username or not game_id:
            return jsonify({'error': 'user_id, username и game_id обязательны'}), 400
        
        game_info, message = lobby_manager.join_game(user_id, username, game_id)
        
        if game_info is None:
            return jsonify({'error': message}), 400
        
        return jsonify({
            'status': 'ok',
            'message': message,
            'game': game_info
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lobby/game/<game_id>', methods=['GET'])
def get_game_info(game_id):
    """Получить информацию об игре"""
    try:
        game_info = lobby_manager.get_game_info(game_id)
        
        if not game_info:
            return jsonify({'error': 'Игра не найдена'}), 404
        
        return jsonify({
            'status': 'ok',
            'game': game_info
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lobby/user/<user_id>', methods=['GET'])
def get_user_game(user_id):
    """Получить информацию об игре пользователя"""
    try:
        user_info = lobby_manager.users.get(user_id)
        
        if not user_info or not user_info.get('current_game'):
            return jsonify({'error': 'У пользователя нет активной игры'}), 404
        
        game_id = user_info['current_game']
        game_info = lobby_manager.get_game_info(game_id)
        
        if not game_info:
            return jsonify({'error': 'Игра не найдена'}), 404
        
        return jsonify({
            'status': 'ok',
            'game': game_info
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lobby/leave', methods=['POST'])
def leave_game():
    """Покинуть игру"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        game_id = data.get('game_id')
        
        if not user_id or not game_id:
            return jsonify({'error': 'user_id и game_id обязательны'}), 400
        
        success, message = lobby_manager.leave_game(user_id, game_id)
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({
            'status': 'ok',
            'message': message
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Export the Flask app for Vercel
app.debug = False

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 