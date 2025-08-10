import json
from typing import Dict, List, Tuple, Optional
from enum import Enum

class CheckerColor(Enum):
    """Цвета шашек"""
    WHITE = "white"
    BLACK = "black"

class CheckerType(Enum):
    """Типы шашек"""
    MAN = "man"      # Обычная шашка
    KING = "king"    # Дамка

class Checker:
    """Класс шашки"""
    
    def __init__(self, color: CheckerColor, position: Tuple[int, int]):
        self.color = color
        self.position = position
        self.type = CheckerType.MAN
        self.is_king = False
    
    def __str__(self):
        return f"{self.color.value}_{self.type.value}"
    
    def get_symbol(self) -> str:
        """Возвращает символ шашки для отображения"""
        if self.color == CheckerColor.WHITE:
            return "⚪" if self.type == CheckerType.MAN else "👑"
        else:
            return "⚫" if self.type == CheckerType.MAN else "👑"
    
    def promote_to_king(self):
        """Превращает шашку в дамку"""
        self.type = CheckerType.KING
        self.is_king = True

class CheckersGame:
    """Класс игры в шашки"""
    
    def __init__(self, white_player_id: int, black_player_id: int):
        self.white_player_id = white_player_id
        self.black_player_id = black_player_id
        self.current_turn = CheckerColor.WHITE
        self.board = self._initialize_board()
        self.game_history = []
        self.game_over = False
        self.winner = None
        self.must_capture = False
        self.capture_chain = []
    
    def _initialize_board(self) -> List[List[Optional[Checker]]]:
        """Инициализирует начальную расстановку шашек"""
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Расставляем черные шашки (верхние 3 ряда)
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:  # Только на черных клетках
                    board[row][col] = Checker(CheckerColor.BLACK, (row, col))
        
        # Расставляем белые шашки (нижние 3 ряда)
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:  # Только на черных клетках
                    board[row][col] = Checker(CheckerColor.WHITE, (row, col))
        
        return board
    
    def get_board_display(self) -> str:
        """Возвращает текстовое представление доски"""
        display = "  a b c d e f g h\n"
        display += "  ─────────────────\n"
        
        for row in range(8):
            display += f"{8-row} │"
            for col in range(8):
                checker = self.board[row][col]
                if checker:
                    display += f"{checker.get_symbol()}"
                else:
                    # Чередуем цвета клеток
                    if (row + col) % 2 == 0:
                        display += "⬜"
                    else:
                        display += "⬛"
                display += "│"
            display += f" {8-row}\n"
        
        display += "  ─────────────────\n"
        display += "  a b c d e f g h\n"
        return display
    
    def is_valid_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Проверяет, является ли ход допустимым"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Проверяем границы доски
        if not (0 <= from_row < 8 and 0 <= from_col < 8 and 0 <= to_row < 8 and 0 <= to_col < 8):
            return False
        
        checker = self.board[from_row][from_col]
        if not checker:
            return False
        
        # Проверяем, что ходит правильный игрок
        if checker.color != self.current_turn:
            return False
        
        # Проверяем, что не ходим на свою шашку
        target_checker = self.board[to_row][to_col]
        if target_checker and target_checker.color == checker.color:
            return False
        
        # Проверяем, что ходим на черную клетку
        if (to_row + to_col) % 2 == 0:
            return False
        
        # Если есть обязательные взятия, проверяем только взятия
        if self.must_capture:
            return self._is_valid_capture(from_pos, to_pos)
        
        # Обычный ход
        return self._is_valid_simple_move(from_pos, to_pos)
    
    def _is_valid_simple_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Проверяет обычный ход (без взятия)"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        checker = self.board[from_row][from_col]
        
        # Проверяем, что клетка назначения пуста
        if self.board[to_row][to_col]:
            return False
        
        row_diff = to_row - from_row
        col_diff = abs(to_col - from_col)
        
        if checker.type == CheckerType.MAN:
            # Обычная шашка ходит только вперед по диагонали на одну клетку
            if checker.color == CheckerColor.WHITE:
                if row_diff != -1:  # Белые ходят вверх
                    return False
            else:  # BLACK
                if row_diff != 1:   # Черные ходят вниз
                    return False
            
            return col_diff == 1
        
        else:  # KING
            # Дамка ходит по диагонали на любое количество клеток
            if abs(row_diff) != abs(col_diff):
                return False
            
            # Проверяем, что путь свободен
            return self._is_path_clear(from_pos, to_pos)
    
    def _is_valid_capture(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Проверяет взятие"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        checker = self.board[from_row][from_col]
        
        # Проверяем, что клетка назначения пуста
        if self.board[to_row][to_col]:
            return False
        
        row_diff = to_row - from_row
        col_diff = to_col - from_col
        
        # Ход должен быть по диагонали
        if abs(row_diff) != abs(col_diff):
            return False
        
        # Находим шашку для взятия
        mid_row = from_row + row_diff // 2
        mid_col = from_col + col_diff // 2
        captured_checker = self.board[mid_row][mid_col]
        
        if not captured_checker or captured_checker.color == checker.color:
            return False
        
        return True
    
    def _is_path_clear(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Проверяет, свободен ли путь между позициями"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Определяем направление движения
        row_step = 1 if to_row > from_row else -1
        col_step = 1 if to_col > from_col else -1
        
        current_row = from_row + row_step
        current_col = from_col + col_step
        
        # Проверяем все клетки на пути (кроме конечной)
        while current_row != to_row and current_col != to_col:
            if self.board[current_row][current_col]:
                return False
            current_row += row_step
            current_col += col_step
        
        return True
    
    def get_valid_moves(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Возвращает список допустимых ходов для шашки на указанной позиции"""
        valid_moves = []
        
        # Если есть обязательные взятия, возвращаем только взятия
        if self.must_capture:
            for row in range(8):
                for col in range(8):
                    if self._is_valid_capture(position, (row, col)):
                        valid_moves.append((row, col))
        else:
            for row in range(8):
                for col in range(8):
                    if self.is_valid_move(position, (row, col)):
                        valid_moves.append((row, col))
        
        return valid_moves
    
    def get_all_captures(self, color: CheckerColor) -> List[Tuple[Tuple[int, int], List[Tuple[int, int]]]]:
        """Возвращает все возможные взятия для цвета"""
        captures = []
        
        for row in range(8):
            for col in range(8):
                checker = self.board[row][col]
                if checker and checker.color == color:
                    capture_moves = []
                    for to_row in range(8):
                        for to_col in range(8):
                            if self._is_valid_capture((row, col), (to_row, to_col)):
                                capture_moves.append((to_row, to_col))
                    
                    if capture_moves:
                        captures.append(((row, col), capture_moves))
        
        return captures
    
    def make_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Выполняет ход"""
        if not self.is_valid_move(from_pos, to_pos):
            return False
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        checker = self.board[from_row][from_col]
        
        # Записываем ход в историю
        move_info = {
            'checker': str(checker),
            'from': self._position_to_notation(from_pos),
            'to': self._position_to_notation(to_pos),
            'turn': self.current_turn.value
        }
        
        # Проверяем, является ли это взятием
        row_diff = to_row - from_row
        col_diff = to_col - from_col
        
        if abs(row_diff) == 2 and abs(col_diff) == 2:
            # Это взятие
            mid_row = from_row + row_diff // 2
            mid_col = from_col + col_diff // 2
            captured_checker = self.board[mid_row][mid_col]
            
            move_info['captured'] = str(captured_checker)
            move_info['capture_pos'] = self._position_to_notation((mid_row, mid_col))
            
            # Удаляем взятую шашку
            self.board[mid_row][mid_col] = None
            
            # Проверяем возможность продолжения взятия
            self.capture_chain.append((to_pos, from_pos))
            
        else:
            # Обычный ход
            self.capture_chain = []
        
        # Выполняем ход
        self.board[to_row][to_col] = checker
        self.board[from_row][from_col] = None
        checker.position = to_pos
        
        # Проверяем превращение в дамку
        self._check_promotion(checker, to_pos)
        
        # Проверяем возможность продолжения взятия
        if self.capture_chain:
            # Проверяем, может ли эта шашка продолжать брать
            if not self.get_all_captures(checker.color):
                # Нет продолжения взятия - меняем ход
                self.current_turn = CheckerColor.BLACK if self.current_turn == CheckerColor.WHITE else CheckerColor.WHITE
                self.capture_chain = []
        else:
            # Обычный ход - меняем ход
            self.current_turn = CheckerColor.BLACK if self.current_turn == CheckerColor.WHITE else CheckerColor.WHITE
        
        self.game_history.append(move_info)
        
        # Проверяем состояние игры
        self._check_game_state()
        
        return True
    
    def _check_promotion(self, checker: Checker, position: Tuple[int, int]):
        """Проверяет превращение шашки в дамку"""
        row, col = position
        
        if checker.color == CheckerColor.WHITE and row == 0:
            checker.promote_to_king()
        elif checker.color == CheckerColor.BLACK and row == 7:
            checker.promote_to_king()
    
    def _check_game_state(self):
        """Проверяет состояние игры"""
        # Проверяем, есть ли обязательные взятия
        self.must_capture = len(self.get_all_captures(self.current_turn)) > 0
        
        # Проверяем, есть ли у текущего игрока возможные ходы
        has_moves = False
        for row in range(8):
            for col in range(8):
                checker = self.board[row][col]
                if checker and checker.color == self.current_turn:
                    if self.get_valid_moves((row, col)):
                        has_moves = True
                        break
            if has_moves:
                break
        
        if not has_moves:
            self.game_over = True
            self.winner = CheckerColor.BLACK if self.current_turn == CheckerColor.WHITE else CheckerColor.WHITE
    
    def _position_to_notation(self, pos: Tuple[int, int]) -> str:
        """Преобразует позицию в нотацию"""
        row, col = pos
        return f"{chr(97 + col)}{8 - row}"
    
    def get_game_status(self) -> str:
        """Возвращает текущий статус игры"""
        if self.game_over:
            winner_name = "Белые" if self.winner == CheckerColor.WHITE else "Черные"
            return f"🏁 Игра окончена! {winner_name} победили!"
        elif self.must_capture:
            current_player = "Белые" if self.current_turn == CheckerColor.WHITE else "Черные"
            return f"⚡ Ход {current_player} (обязательное взятие)"
        else:
            current_player = "Белые" if self.current_turn == CheckerColor.WHITE else "Черные"
            return f"🎯 Ход {current_player}"
        
        return "🎮 Игра продолжается"
    
    def get_game_summary(self) -> Dict:
        """Возвращает сводку игры"""
        return {
            'white_player': self.white_player_id,
            'black_player': self.black_player_id,
            'current_turn': self.current_turn.value,
            'game_over': self.game_over,
            'winner': self.winner.value if self.winner else None,
            'must_capture': self.must_capture,
            'moves_count': len(self.game_history),
            'status': self.get_game_status()
        } 