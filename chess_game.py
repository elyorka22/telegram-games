import json
from typing import Dict, List, Tuple, Optional
from enum import Enum

class PieceType(Enum):
    """Типы шахматных фигур"""
    PAWN = "pawn"
    ROOK = "rook"
    KNIGHT = "knight"
    BISHOP = "bishop"
    QUEEN = "queen"
    KING = "king"

class Color(Enum):
    """Цвета фигур"""
    WHITE = "white"
    BLACK = "black"

class ChessPiece:
    """Класс шахматной фигуры"""
    
    def __init__(self, piece_type: PieceType, color: Color, position: Tuple[int, int]):
        self.type = piece_type
        self.color = color
        self.position = position
        self.has_moved = False  # Для рокировки и первого хода пешки
    
    def __str__(self):
        return f"{self.color.value}_{self.type.value}"
    
    def get_symbol(self) -> str:
        """Возвращает символ фигуры для отображения"""
        symbols = {
            PieceType.PAWN: "♟️" if self.color == Color.WHITE else "♙",
            PieceType.ROOK: "♜" if self.color == Color.WHITE else "♖",
            PieceType.KNIGHT: "♞" if self.color == Color.WHITE else "♘",
            PieceType.BISHOP: "♝" if self.color == Color.WHITE else "♗",
            PieceType.QUEEN: "♛" if self.color == Color.WHITE else "♕",
            PieceType.KING: "♚" if self.color == Color.WHITE else "♔"
        }
        return symbols.get(self.type, "?")

class ChessGame:
    """Класс шахматной игры"""
    
    def __init__(self, white_player_id: int, black_player_id: int):
        self.white_player_id = white_player_id
        self.black_player_id = black_player_id
        self.current_turn = Color.WHITE
        self.board = self._initialize_board()
        self.game_history = []
        self.game_over = False
        self.winner = None
        self.check = False
        self.checkmate = False
        self.stalemate = False
    
    def _initialize_board(self) -> List[List[Optional[ChessPiece]]]:
        """Инициализирует начальную расстановку фигур"""
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Расставляем пешки
        for col in range(8):
            board[1][col] = ChessPiece(PieceType.PAWN, Color.BLACK, (1, col))
            board[6][col] = ChessPiece(PieceType.PAWN, Color.WHITE, (6, col))
        
        # Расставляем остальные фигуры
        pieces = [
            (PieceType.ROOK, 0),
            (PieceType.KNIGHT, 1),
            (PieceType.BISHOP, 2),
            (PieceType.QUEEN, 3),
            (PieceType.KING, 4),
            (PieceType.BISHOP, 5),
            (PieceType.KNIGHT, 6),
            (PieceType.ROOK, 7)
        ]
        
        for piece_type, col in pieces:
            board[0][col] = ChessPiece(piece_type, Color.BLACK, (0, col))
            board[7][col] = ChessPiece(piece_type, Color.WHITE, (7, col))
        
        return board
    
    def get_board_display(self) -> str:
        """Возвращает текстовое представление доски"""
        display = "  a b c d e f g h\n"
        display += "  ─────────────────\n"
        
        for row in range(8):
            display += f"{8-row} │"
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    display += f"{piece.get_symbol()}"
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
        
        piece = self.board[from_row][from_col]
        if not piece:
            return False
        
        # Проверяем, что ходит правильный игрок
        if piece.color != self.current_turn:
            return False
        
        # Проверяем, что не ходим на свою фигуру
        target_piece = self.board[to_row][to_col]
        if target_piece and target_piece.color == piece.color:
            return False
        
        # Проверяем правила движения для каждого типа фигуры
        if not self._can_piece_move_to(piece, from_pos, to_pos):
            return False
        
        # Проверяем, что ход не ставит короля под шах
        if self._would_move_cause_check(from_pos, to_pos):
            return False
        
        return True
    
    def _can_piece_move_to(self, piece: ChessPiece, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Проверяет, может ли фигура ходить на указанную позицию по правилам"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        if piece.type == PieceType.PAWN:
            return self._can_pawn_move_to(piece, from_pos, to_pos)
        elif piece.type == PieceType.ROOK:
            return self._can_rook_move_to(from_pos, to_pos)
        elif piece.type == PieceType.KNIGHT:
            return self._can_knight_move_to(from_pos, to_pos)
        elif piece.type == PieceType.BISHOP:
            return self._can_bishop_move_to(from_pos, to_pos)
        elif piece.type == PieceType.QUEEN:
            return self._can_queen_move_to(from_pos, to_pos)
        elif piece.type == PieceType.KING:
            return self._can_king_move_to(piece, from_pos, to_pos)
        
        return False
    
    def _can_pawn_move_to(self, piece: ChessPiece, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Проверяет ход пешки"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        direction = 1 if piece.color == Color.BLACK else -1
        start_row = 1 if piece.color == Color.BLACK else 6
        
        # Обычный ход вперед
        if from_col == to_col and to_row == from_row + direction and not self.board[to_row][to_col]:
            return True
        
        # Первый ход пешки (может ходить на 2 клетки)
        if from_col == to_col and from_row == start_row and to_row == from_row + 2 * direction:
            if not self.board[from_row + direction][from_col] and not self.board[to_row][to_col]:
                return True
        
        # Взятие по диагонали
        if abs(to_col - from_col) == 1 and to_row == from_row + direction:
            if self.board[to_row][to_col]:
                return True
        
        return False
    
    def _can_rook_move_to(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Проверяет ход ладьи"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Ладья ходит по прямой
        if from_row != to_row and from_col != to_col:
            return False
        
        # Проверяем, что путь свободен
        return self._is_path_clear(from_pos, to_pos)
    
    def _can_knight_move_to(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Проверяет ход коня"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Конь ходит буквой Г
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
    
    def _can_bishop_move_to(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Проверяет ход слона"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Слон ходит по диагонали
        if abs(to_row - from_row) != abs(to_col - from_col):
            return False
        
        # Проверяем, что путь свободен
        return self._is_path_clear(from_pos, to_pos)
    
    def _can_queen_move_to(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Проверяет ход ферзя"""
        # Ферзь ходит как ладья + слон
        return (self._can_rook_move_to(from_pos, to_pos) or 
                self._can_bishop_move_to(from_pos, to_pos))
    
    def _can_king_move_to(self, piece: ChessPiece, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Проверяет ход короля"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Король ходит на одну клетку в любом направлении
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        return row_diff <= 1 and col_diff <= 1
    
    def _is_path_clear(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Проверяет, свободен ли путь между позициями"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Определяем направление движения
        row_step = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_step = 0 if from_col == to_col else (1 if to_col > from_col else -1)
        
        current_row = from_row + row_step
        current_col = from_col + col_step
        
        # Проверяем все клетки на пути (кроме конечной)
        while current_row != to_row or current_col != to_col:
            if self.board[current_row][current_col]:
                return False
            current_row += row_step
            current_col += col_step
        
        return True
    
    def _would_move_cause_check(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Проверяет, не ставит ли ход короля под шах"""
        # Временно делаем ход
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Сохраняем состояние
        original_piece = self.board[to_row][to_col]
        moving_piece = self.board[from_row][from_col]
        
        # Делаем ход
        self.board[to_row][to_col] = moving_piece
        self.board[from_row][from_col] = None
        if moving_piece:
            moving_piece.position = to_pos
        
        # Проверяем, под шахом ли король
        in_check = self._is_king_in_check(self.current_turn)
        
        # Отменяем ход
        self.board[from_row][from_col] = moving_piece
        self.board[to_row][to_col] = original_piece
        if moving_piece:
            moving_piece.position = from_pos
        
        return in_check
    
    def _is_king_in_check(self, color: Color) -> bool:
        """Проверяет, под шахом ли король указанного цвета"""
        # Находим короля
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.type == PieceType.KING and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return False
        
        # Проверяем, может ли какая-либо фигура противника атаковать короля
        opponent_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == opponent_color:
                    if self._can_piece_move_to(piece, (row, col), king_pos):
                        return True
        
        return False
    
    def make_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Выполняет ход"""
        if not self.is_valid_move(from_pos, to_pos):
            return False
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.board[from_row][from_col]
        captured_piece = self.board[to_row][to_col]
        
        # Записываем ход в историю
        move_info = {
            'piece': str(piece),
            'from': self._position_to_notation(from_pos),
            'to': self._position_to_notation(to_pos),
            'captured': str(captured_piece) if captured_piece else None,
            'turn': self.current_turn.value
        }
        self.game_history.append(move_info)
        
        # Выполняем ход
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        piece.position = to_pos
        piece.has_moved = True
        
        # Проверяем специальные ходы
        self._check_special_moves(piece, from_pos, to_pos)
        
        # Меняем ход
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        
        # Проверяем состояние игры
        self._check_game_state()
        
        return True
    
    def _check_special_moves(self, piece: ChessPiece, from_pos: Tuple[int, int], to_pos: Tuple[int, int]):
        """Проверяет специальные ходы (превращение пешки, рокировка)"""
        # Превращение пешки
        if piece.type == PieceType.PAWN:
            if (piece.color == Color.WHITE and to_pos[0] == 0) or \
               (piece.color == Color.BLACK and to_pos[0] == 7):
                # Автоматически превращаем в ферзя
                piece.type = PieceType.QUEEN
    
    def _check_game_state(self):
        """Проверяет состояние игры (шах, мат, пат)"""
        # Проверяем, под шахом ли текущий игрок
        self.check = self._is_king_in_check(self.current_turn)
        
        if self.check:
            # Проверяем на мат
            if self._is_checkmate():
                self.checkmate = True
                self.game_over = True
                self.winner = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        else:
            # Проверяем на пат
            if self._is_stalemate():
                self.stalemate = True
                self.game_over = True
    
    def _is_checkmate(self) -> bool:
        """Проверяет, есть ли мат"""
        # Если король под шахом и нет возможных ходов
        if not self.check:
            return False
        
        # Проверяем все возможные ходы текущего игрока
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == self.current_turn:
                    for to_row in range(8):
                        for to_col in range(8):
                            if self.is_valid_move((row, col), (to_row, to_col)):
                                return False
        
        return True
    
    def _is_stalemate(self) -> bool:
        """Проверяет, есть ли пат"""
        # Если король не под шахом, но нет возможных ходов
        if self.check:
            return False
        
        # Проверяем все возможные ходы текущего игрока
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == self.current_turn:
                    for to_row in range(8):
                        for to_col in range(8):
                            if self.is_valid_move((row, col), (to_row, to_col)):
                                return False
        
        return True
    
    def _position_to_notation(self, pos: Tuple[int, int]) -> str:
        """Преобразует позицию в шахматную нотацию"""
        row, col = pos
        return f"{chr(97 + col)}{8 - row}"
    
    def get_game_status(self) -> str:
        """Возвращает текущий статус игры"""
        if self.game_over:
            if self.checkmate:
                winner_name = "Белые" if self.winner == Color.WHITE else "Черные"
                return f"🏁 Мат! {winner_name} победили!"
            elif self.stalemate:
                return "🤝 Пат! Ничья!"
        elif self.check:
            return "⚠️ Шах!"
        else:
            current_player = "Белые" if self.current_turn == Color.WHITE else "Черные"
            return f"🎯 Ход {current_player}"
        
        return "🎮 Игра продолжается"
    
    def get_valid_moves(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Возвращает список допустимых ходов для фигуры на указанной позиции"""
        valid_moves = []
        for row in range(8):
            for col in range(8):
                if self.is_valid_move(position, (row, col)):
                    valid_moves.append((row, col))
        return valid_moves
    
    def get_game_summary(self) -> Dict:
        """Возвращает сводку игры"""
        return {
            'white_player': self.white_player_id,
            'black_player': self.black_player_id,
            'current_turn': self.current_turn.value,
            'game_over': self.game_over,
            'winner': self.winner.value if self.winner else None,
            'check': self.check,
            'checkmate': self.checkmate,
            'stalemate': self.stalemate,
            'moves_count': len(self.game_history),
            'status': self.get_game_status()
        } 