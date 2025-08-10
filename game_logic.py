import random
from typing import Dict, List, Tuple
from game_data import QUIZ_QUESTIONS, WELCOME_MESSAGES, RESULT_MESSAGES

class QuizGame:
    """Класс для управления игрой-викториной"""
    
    def __init__(self):
        self.active_games: Dict[int, Dict] = {}  # user_id -> game_state
        self.user_scores: Dict[int, int] = {}    # user_id -> total_score
    
    def start_game(self, user_id: int) -> Tuple[str, List[List]]:
        """Начинает новую игру для пользователя"""
        # Перемешиваем вопросы
        questions = QUIZ_QUESTIONS.copy()
        random.shuffle(questions)
        
        # Создаем состояние игры
        game_state = {
            'current_question': 0,
            'questions': questions,
            'score': 0,
            'answers': []
        }
        
        self.active_games[user_id] = game_state
        
        # Формируем первое сообщение
        welcome = random.choice(WELCOME_MESSAGES)
        first_question = self._format_question(questions[0], 0)
        
        return welcome + "\n\n" + first_question, self._create_keyboard(questions[0])
    
    def process_answer(self, user_id: int, answer_index: int) -> Tuple[str, List[List], bool]:
        """Обрабатывает ответ пользователя"""
        if user_id not in self.active_games:
            return "Игра не найдена. Начните новую игру командой /start", [], False
        
        game_state = self.active_games[user_id]
        current_q = game_state['current_question']
        question = game_state['questions'][current_q]
        
        # Проверяем ответ
        is_correct = answer_index == question['correct']
        if is_correct:
            game_state['score'] += 1
        
        game_state['answers'].append(answer_index)
        
        # Формируем сообщение о результате
        result_text = self._format_answer_result(question, is_correct, answer_index)
        
        # Переходим к следующему вопросу
        game_state['current_question'] += 1
        
        if game_state['current_question'] >= len(game_state['questions']):
            # Игра окончена
            return self._finish_game(user_id), [], True
        else:
            # Показываем следующий вопрос
            next_question = self._format_question(
                game_state['questions'][game_state['current_question']], 
                game_state['current_question']
            )
            full_text = result_text + "\n\n" + next_question
            return full_text, self._create_keyboard(game_state['questions'][game_state['current_question']]), False
    
    def _format_question(self, question: Dict, question_num: int) -> str:
        """Форматирует вопрос для отображения"""
        return f"❓ Вопрос {question_num + 1}:\n{question['question']}"
    
    def _create_keyboard(self, question: Dict) -> List[List]:
        """Создает клавиатуру с вариантами ответов"""
        from telegram import InlineKeyboardButton
        
        keyboard = []
        for i, option in enumerate(question['options']):
            keyboard.append([InlineKeyboardButton(option, callback_data=f"answer_{i}")])
        
        return keyboard
    
    def _format_answer_result(self, question: Dict, is_correct: bool, user_answer: int) -> str:
        """Форматирует результат ответа"""
        if is_correct:
            result = "✅ Правильно!"
        else:
            correct_answer = question['options'][question['correct']]
            result = f"❌ Неправильно! Правильный ответ: {correct_answer}"
        
        explanation = f"\n💡 {question['explanation']}"
        return result + explanation
    
    def _finish_game(self, user_id: int) -> str:
        """Завершает игру и показывает результаты"""
        game_state = self.active_games[user_id]
        score = game_state['score']
        total = len(game_state['questions'])
        
        # Обновляем общий счет пользователя
        if user_id not in self.user_scores:
            self.user_scores[user_id] = 0
        self.user_scores[user_id] += score
        
        # Определяем категорию результата
        percentage = (score / total) * 100
        if percentage == 100:
            category = "perfect"
        elif percentage >= 80:
            category = "good"
        elif percentage >= 60:
            category = "average"
        else:
            category = "poor"
        
        # Формируем итоговое сообщение
        result_message = random.choice(RESULT_MESSAGES[category])
        
        final_text = f"""
🏁 Игра окончена!

📊 Ваш результат: {score}/{total} ({percentage:.1f}%)
{result_message}

🎯 Общий счет: {self.user_scores[user_id]}

🔄 Начните новую игру командой /start
        """.strip()
        
        # Удаляем завершенную игру
        del self.active_games[user_id]
        
        return final_text
    
    def get_leaderboard(self) -> List[Tuple[int, int]]:
        """Возвращает таблицу лидеров"""
        sorted_scores = sorted(self.user_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:10]  # Топ-10 игроков
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Возвращает статистику пользователя"""
        total_score = self.user_scores.get(user_id, 0)
        games_played = len([game for game in self.active_games.values() if game.get('user_id') == user_id])
        
        return {
            'total_score': total_score,
            'games_played': games_played,
            'current_game': user_id in self.active_games
        } 