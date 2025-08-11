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

# Файл для persistent storage
STORAGE_FILE = 'lobby_data.json'

def load_storage():
    """Загрузить данные из файла"""
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                LOBBY_STORAGE['games'] = data.get('games', {})
                LOBBY_STORAGE['users'] = data.get('users', {})
                print(f"Загружено {len(LOBBY_STORAGE['games'])} игр и {len(LOBBY_STORAGE['users'])} пользователей")
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")

def save_storage():
    """Сохранить данные в файл"""
    try:
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(LOBBY_STORAGE, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения данных: {e}")

# Загружаем данные при запуске
load_storage()

class LobbyManager:
    def __init__(self):
        self.games = LOBBY_STORAGE['games']
        self.users = LOBBY_STORAGE['users']
    
    def create_game(self, user_id, username, game_type):
        """Создать новую игру"""
        game_id = str(uuid.uuid4())[:8]
        # Приводим user_id к строке для корректного сравнения
        user_id = str(user_id)
        
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
        
        # Сохраняем данные
        save_storage()
        
        return game_info
    
    def join_game(self, user_id, username, game_id):
        """Присоединиться к игре"""
        # Приводим user_id к строке для корректного сравнения
        user_id = str(user_id)
        
        if game_id not in self.games:
            return None, "Игра не найдена"
        
        game = self.games[game_id]
        
        if game['status'] != 'waiting':
            return None, "Игра уже началась"
        
        if len(game['players']) >= game['max_players']:
            return None, "Игра заполнена"
        
        # Проверяем, не в игре ли уже пользователь
        for player in game['players']:
            if str(player['id']) == user_id:
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
        
        # Сохраняем данные
        save_storage()
        
        return game, "Успешно присоединились"
    
    def get_available_games(self):
        """Получить список доступных игр"""
        print(f"DEBUG: get_available_games - всего игр в системе: {len(self.games)}")
        
        available = []
        for game_id, game in self.games.items():
            print(f"DEBUG: Проверяем игру {game_id} - статус: {game['status']}, игроков: {len(game['players'])}/{game['max_players']}")
            
            if game['status'] == 'waiting' and len(game['players']) < game['max_players']:
                available.append({
                    'id': game_id,
                    'type': game['type'],
                    'creator': game['creator']['username'],
                    'players_count': len(game['players']),
                    'max_players': game['max_players'],
                    'created_at': game['created_at']
                })
                print(f"DEBUG: Игра {game_id} добавлена в доступные")
        
        print(f"DEBUG: Доступных игр: {len(available)}")
        return available
    
    def create_user(self, user_id, username):
        """Создать пользователя если его нет в системе"""
        user_id = str(user_id)
        
        if user_id not in self.users:
            self.users[user_id] = {
                'username': username,
                'current_game': None,
                'created_at': datetime.now().isoformat()
            }
            save_storage()
            print(f"DEBUG: Создан новый пользователь {user_id} ({username})")
            return True
        else:
            print(f"DEBUG: Пользователь {user_id} уже существует")
            return False
    
    def get_or_create_user(self, user_id, username):
        """Получить пользователя или создать его если не существует"""
        user_id = str(user_id)
        
        if user_id not in self.users:
            return self.create_user(user_id, username)
        
        return self.users[user_id]
    
    def get_game_info(self, game_id):
        """Получить информацию об игре"""
        return self.games.get(game_id)
    
    def leave_game(self, user_id, game_id):
        """Покинуть игру"""
        # Приводим user_id к строке для корректного сравнения
        user_id = str(user_id)
        
        if game_id not in self.games:
            return False, "Игра не найдена"
        
        game = self.games[game_id]
        
        # Удаляем игрока из игры
        game['players'] = [p for p in game['players'] if str(p['id']) != user_id]
        
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
        
        # Сохраняем данные
        save_storage()
        
        return True, "Успешно покинули игру"
    
    def cleanup_old_games(self):
        """Очистка старых игр"""
        print(f"DEBUG: cleanup_old_games - начинаем очистку")
        current_time = datetime.now()
        games_to_remove = []
        
        for game_id, game in self.games.items():
            created_time = datetime.fromisoformat(game['created_at'])
            time_diff = (current_time - created_time).seconds
            print(f"DEBUG: Игра {game_id} создана {time_diff} секунд назад")
            
            if time_diff > 3600:  # 1 час
                games_to_remove.append(game_id)
                print(f"DEBUG: Игра {game_id} будет удалена (старше 1 часа)")
        
        for game_id in games_to_remove:
            del self.games[game_id]
            print(f"DEBUG: Игра {game_id} удалена")
        
        print(f"DEBUG: Очистка завершена, осталось игр: {len(self.games)}")
        save_storage() # Добавляем сохранение после очистки

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
        print(f"DEBUG: Запрос списка игр")
        
        # Очищаем старые игры
        lobby_manager.cleanup_old_games()
        
        games = lobby_manager.get_available_games()
        print(f"DEBUG: Найдено игр: {len(games)}")
        
        return jsonify({
            'status': 'ok',
            'games': games,
            'count': len(games)
        })
    except Exception as e:
        print(f"DEBUG: Ошибка при получении игр: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/lobby/create', methods=['POST'])
def create_game():
    """Создать новую игру"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        username = data.get('username')
        game_type = data.get('game_type', 'chess')
        
        print(f"DEBUG: Создание игры - user_id: {user_id}, username: {username}, game_type: {game_type}")
        
        if not user_id or not username:
            print(f"DEBUG: Ошибка - отсутствуют user_id или username")
            return jsonify({'error': 'user_id и username обязательны'}), 400
        
        # Приводим user_id к строке
        user_id = str(user_id)
        
        game_info = lobby_manager.create_game(user_id, username, game_type)
        
        print(f"DEBUG: Игра создана успешно - game_id: {game_info['id']}")
        
        return jsonify({
            'status': 'ok',
            'message': 'Игра создана',
            'game': game_info
        })
    except Exception as e:
        print(f"DEBUG: Ошибка при создании игры: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/lobby/join', methods=['POST'])
def join_game():
    """Присоединиться к игре"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        username = data.get('username')
        game_id = data.get('game_id')
        
        print(f"DEBUG: Присоединение к игре - user_id: {user_id}, username: {username}, game_id: {game_id}")
        
        if not user_id or not username or not game_id:
            print(f"DEBUG: Ошибка - отсутствуют обязательные параметры")
            return jsonify({'error': 'user_id, username и game_id обязательны'}), 400
        
        # Приводим user_id к строке
        user_id = str(user_id)
        
        game_info, message = lobby_manager.join_game(user_id, username, game_id)
        
        print(f"DEBUG: Результат присоединения - game_info: {game_info is not None}, message: {message}")
        
        if game_info is None:
            return jsonify({'error': message}), 400
        
        return jsonify({
            'status': 'ok',
            'message': message,
            'game': game_info
        })
    except Exception as e:
        print(f"DEBUG: Ошибка при присоединении к игре: {str(e)}")
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

@app.route('/api/lobby/user/create', methods=['POST'])
def create_user():
    """Создать нового пользователя"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        username = data.get('username')
        
        if not user_id or not username:
            return jsonify({'error': 'user_id и username обязательны'}), 400
        
        # Приводим user_id к строке
        user_id = str(user_id)
        
        created = lobby_manager.create_user(user_id, username)
        
        return jsonify({
            'status': 'ok',
            'created': created,
            'message': 'Пользователь создан' if created else 'Пользователь уже существует',
            'user_id': user_id,
            'username': username
        })
    except Exception as e:
        print(f"DEBUG: Ошибка при создании пользователя: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/lobby/user/<user_id>', methods=['GET'])
def get_user_game(user_id):
    """Получить информацию об игре пользователя"""
    try:
        # Приводим user_id к строке
        user_id = str(user_id)
        
        print(f"DEBUG: Запрос информации о пользователе {user_id}")
        print(f"DEBUG: Всего пользователей в системе: {len(lobby_manager.users)}")
        print(f"DEBUG: Пользователи: {list(lobby_manager.users.keys())}")
        
        user_info = lobby_manager.users.get(user_id)
        
        if not user_info:
            print(f"DEBUG: Пользователь {user_id} не найден в системе")
            return jsonify({
                'status': 'not_found',
                'message': 'Пользователь не найден в системе',
                'user_id': user_id,
                'has_active_game': False
            }), 200  # Возвращаем 200 вместо 404 для лучшего UX
        
        if not user_info.get('current_game'):
            print(f"DEBUG: У пользователя {user_id} нет активной игры")
            return jsonify({
                'status': 'no_game',
                'message': 'У пользователя нет активной игры',
                'user_id': user_id,
                'username': user_info.get('username'),
                'has_active_game': False
            }), 200
        
        game_id = user_info['current_game']
        game_info = lobby_manager.get_game_info(game_id)
        
        if not game_info:
            print(f"DEBUG: Игра {game_id} не найдена для пользователя {user_id}")
            return jsonify({
                'status': 'game_not_found',
                'message': 'Игра не найдена',
                'user_id': user_id,
                'game_id': game_id,
                'has_active_game': False
            }), 200
        
        print(f"DEBUG: Найдена активная игра {game_id} для пользователя {user_id}")
        return jsonify({
            'status': 'ok',
            'game': game_info,
            'user_id': user_id,
            'has_active_game': True
        })
    except Exception as e:
        print(f"DEBUG: Ошибка при получении информации о пользователе {user_id}: {str(e)}")
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
        
        # Приводим user_id к строке
        user_id = str(user_id)
        
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