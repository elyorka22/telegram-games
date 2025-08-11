// JavaScript для страницы игры в шахматы и шашки

let socket = null;
let gameId = null;
let playerColor = null;
let gameType = null;
let gameMode = null;
let board = [];
let selectedSquare = null;
let validMoves = [];
let moveHistory = [];
let telegramWebApp = null;
let isTelegramApp = false;
let isComputerTurn = false;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initializeTelegramWebApp();
    initializeSocket();
    createGameBoard();
    setupEventListeners();
    setupTelegramUI();
});

// Инициализация Telegram WebApp
function initializeTelegramWebApp() {
    // Проверяем, запущено ли приложение в Telegram
    try {
        if (window.Telegram && window.Telegram.WebApp) {
            telegramWebApp = window.Telegram.WebApp;
            isTelegramApp = true;
            
            console.log('Telegram Web App инициализирован в игре');
            
            // Переопределяем проблемные методы
            if (telegramWebApp.showPopup) {
                const originalShowPopup = telegramWebApp.showPopup;
                telegramWebApp.showPopup = function(message) {
                    console.log('showPopup called in game.js, using alert instead');
                    return alert(message); // Используем alert напрямую
                };
            }
            
            // Инициализируем Telegram Web App
            telegramWebApp.ready();
            
            // Настраиваем тему
            if (telegramWebApp.themeParams) {
                applyTelegramTheme(telegramWebApp.themeParams);
            }
            
            // Слушаем изменения темы
            telegramWebApp.onEvent('themeChanged', function() {
                applyTelegramTheme(telegramWebApp.themeParams);
            });
            
            // Расширяем приложение на всю высоту
            telegramWebApp.expand();
            
            // Настраиваем главную кнопку
            setupMainButton();
        }
    } catch (e) {
        console.log('Telegram WebApp not available in game, using fallback');
        telegramWebApp = {
            showAlert: (message) => alert(message),
            showPopup: (message) => alert(message),
            expand: () => {},
            ready: () => {},
            initDataUnsafe: { user: null }
        };
    }
}

// Применение темы Telegram
function applyTelegramTheme(themeParams) {
    if (!themeParams) return;
    
    const root = document.documentElement;
    
    // Применяем цвета темы как CSS переменные
    if (themeParams.bg_color) {
        root.style.setProperty('--tg-theme-bg-color', themeParams.bg_color);
    }
    if (themeParams.text_color) {
        root.style.setProperty('--tg-theme-text-color', themeParams.text_color);
    }
    if (themeParams.button_color) {
        root.style.setProperty('--tg-theme-button-color', themeParams.button_color);
    }
    if (themeParams.button_text_color) {
        root.style.setProperty('--tg-theme-button-text-color', themeParams.button_text_color);
    }
    if (themeParams.secondary_bg_color) {
        root.style.setProperty('--tg-theme-secondary-bg-color', themeParams.secondary_bg_color);
    }
    
    // Применяем стили к элементам
    document.body.style.backgroundColor = themeParams.bg_color || '#ffffff';
    document.body.style.color = themeParams.text_color || '#000000';
}

// Настройка UI для Telegram
function setupTelegramUI() {
    if (!isTelegramApp) return;
    
    // Настраиваем кнопки для Telegram
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.style.backgroundColor = telegramWebApp.themeParams?.button_color || '#2481cc';
        button.style.color = telegramWebApp.themeParams?.button_text_color || '#ffffff';
    });
}

// Настройка главной кнопки Telegram
function setupMainButton() {
    if (!isTelegramApp || !telegramWebApp.MainButton) return;
    
    telegramWebApp.MainButton.setText('Сдаться');
    telegramWebApp.MainButton.onClick(function() {
        if (confirm('Вы уверены, что хотите сдаться?')) {
            // Логика сдачи
            if (isTelegramApp && telegramWebApp.showAlert) {
                telegramWebApp.showAlert('Вы сдались');
            }
        }
    });
}

// Показать главную кнопку
function showMainButton() {
    if (isTelegramApp && telegramWebApp.MainButton) {
        telegramWebApp.MainButton.show();
    }
}

// Скрыть главную кнопку
function hideMainButton() {
    if (isTelegramApp && telegramWebApp.MainButton) {
        telegramWebApp.MainButton.hide();
    }
}

// Инициализация WebSocket соединения
function initializeSocket() {
    // Устанавливаем глобальные переменные
    gameId = GAME_ID;
    gameType = GAME_TYPE;
    gameMode = GAME_MODE;
    
    // Если это игра с компьютером, показываем доску сразу
    if (gameMode === 'computer') {
        console.log('Режим игры с компьютером');
        showComputerGame();
        return;
    }
    
    // В production WebSocket может быть недоступен, поэтому используем fallback
    if (window.location.hostname === 'telegram-games-two.vercel.app') {
        console.log('Production режим - используем fallback без WebSocket');
        showStaticBoard();
        return;
    }
    
    // Подключаемся к WebSocket серверу игр только в development
    socket = io('http://localhost:5002');
    
    socket.on('connect', function() {
        console.log('Подключен к серверу игры');
        
        // Получаем данные пользователя
        const user = window.Telegram?.WebApp?.initDataUnsafe?.user || {
            id: Math.floor(Math.random() * 1000000),
            username: 'Player' + Math.floor(Math.random() * 1000)
        };
        
        // Присоединяемся к игре
        socket.emit('join_game', { 
            game_id: GAME_ID,
            game_type: GAME_TYPE,
            player_id: user.id
        });
    });
    
    socket.on('connect_error', function(error) {
        console.log('Ошибка подключения к WebSocket:', error);
        // Fallback: показываем статичную доску
        showStaticBoard();
    });
    
    socket.on('game_joined', function(data) {
        console.log('Присоединился к игре:', data);
        gameId = data.game_id;
        playerColor = data.color;
        gameType = data.game_type;
        updateBoard(data.board);
        updateGameStatus(data.status);
        updatePlayerStatus();
        updateGameTitle();
        
        // Показываем главную кнопку в Telegram
        showMainButton();
    });
    
    socket.on('move_made', function(data) {
        console.log('Ход сделан:', data);
        updateBoard(data.board);
        updateGameStatus(data.status);
        addMoveToHistory(data);
        clearSelection();
        
        if (data.game_over) {
            showGameOver(data.winner);
            // Скрываем главную кнопку в Telegram
            hideMainButton();
        }
    });
    
    socket.on('valid_moves', function(data) {
        validMoves = data.moves;
        highlightValidMoves();
    });
    
    socket.on('error', function(data) {
        showError(data.message);
        
        // В Telegram показываем ошибку
        if (isTelegramApp && telegramWebApp.showAlert) {
            telegramWebApp.showAlert('Ошибка: ' + data.message);
        }
    });
    
    socket.on('opponent_disconnected', function() {
        showError('Противник отключился');
        
        // В Telegram показываем уведомление
        if (isTelegramApp && telegramWebApp.showAlert) {
            telegramWebApp.showAlert('Противник отключился');
        }
        
        setTimeout(() => {
            if (isTelegramApp) {
                telegramWebApp.close();
            } else {
                window.location.href = '/';
            }
        }, 3000);
    });
}

// Fallback функция для показа статичной доски
function showStaticBoard() {
    console.log('Показываем статичную доску (WebSocket недоступен)');
    
    // Устанавливаем базовые значения
    gameId = GAME_ID;
    gameType = GAME_TYPE;
    playerColor = 'white'; // По умолчанию белые
    
    // Создаем начальную расстановку шахмат
    const initialBoard = createInitialChessBoard();
    updateBoard(initialBoard);
    
    // Обновляем UI
    updateGameStatus('Игра началась (локальный режим)');
    updatePlayerStatus();
    updateGameTitle();
    
    // Показываем уведомление
    if (isTelegramApp && telegramWebApp.showAlert) {
        telegramWebApp.showAlert('Игра началась! WebSocket недоступен, игра в локальном режиме.');
    }
    
    // Показываем главную кнопку
    showMainButton();
}

// Создание начальной расстановки шахмат
function createInitialChessBoard() {
    const board = Array(8).fill(null).map(() => Array(8).fill(null));
    
    // Расставляем пешки
    for (let col = 0; col < 8; col++) {
        board[1][col] = { color: 'black', type: 'pawn', symbol: '♙' };
        board[6][col] = { color: 'white', type: 'pawn', symbol: '♟️' };
    }
    
    // Расставляем остальные фигуры
    const pieces = [
        { type: 'rook', symbol: '♖', whiteSymbol: '♜' },
        { type: 'knight', symbol: '♘', whiteSymbol: '♞' },
        { type: 'bishop', symbol: '♗', whiteSymbol: '♝' },
        { type: 'queen', symbol: '♕', whiteSymbol: '♛' },
        { type: 'king', symbol: '♔', whiteSymbol: '♚' },
        { type: 'bishop', symbol: '♗', whiteSymbol: '♝' },
        { type: 'knight', symbol: '♘', whiteSymbol: '♞' },
        { type: 'rook', symbol: '♖', whiteSymbol: '♜' }
    ];
    
    for (let col = 0; col < 8; col++) {
        const piece = pieces[col];
        board[0][col] = { color: 'black', type: piece.type, symbol: piece.symbol };
        board[7][col] = { color: 'white', type: piece.type, symbol: piece.whiteSymbol };
    }
    
    return board;
}

// Создание игровой доски
function createGameBoard() {
    const gameBoard = document.getElementById('chessBoard');
    
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const square = document.createElement('div');
            square.className = `chess-square ${(row + col) % 2 === 0 ? 'white' : 'black'}`;
            square.dataset.row = row;
            square.dataset.col = col;
            
            square.addEventListener('click', function() {
                handleSquareClick(row, col);
            });
            
            gameBoard.appendChild(square);
        }
    }
}

// Обработка клика по клетке
function handleSquareClick(row, col) {
    const square = getSquare(row, col);
    
    if (selectedSquare) {
        // Если уже выбрана клетка, пытаемся сделать ход
        const fromRow = parseInt(selectedSquare.dataset.row);
        const fromCol = parseInt(selectedSquare.dataset.col);
        
        if (fromRow === row && fromCol === col) {
            // Кликнули на ту же клетку - отменяем выбор
            clearSelection();
        } else {
            // Пытаемся сделать ход
            makeMove(fromRow, fromCol, row, col);
        }
    } else {
        // Выбираем клетку
        selectSquare(row, col);
    }
}

// Выбор клетки
function selectSquare(row, col) {
    clearSelection();
    selectedSquare = getSquare(row, col);
    selectedSquare.classList.add('selected');
    
    // Запрашиваем допустимые ходы
    socket.emit('get_valid_moves', {
        game_id: gameId,
        position: [row, col]
    });
}

// Очистка выбора
function clearSelection() {
    if (selectedSquare) {
        selectedSquare.classList.remove('selected');
        selectedSquare = null;
    }
    clearValidMoves();
}

// Подсветка допустимых ходов
function highlightValidMoves() {
    validMoves.forEach(pos => {
        const square = getSquare(pos[0], pos[1]);
        square.classList.add('valid-move');
    });
}

// Очистка подсветки допустимых ходов
function clearValidMoves() {
    document.querySelectorAll('.valid-move').forEach(square => {
        square.classList.remove('valid-move');
    });
    validMoves = [];
}

// Выполнение хода
function makeMove(fromRow, fromCol, toRow, toCol) {
    // Получаем данные пользователя
    const user = window.Telegram?.WebApp?.initDataUnsafe?.user || {
        id: Math.floor(Math.random() * 1000000)
    };
    
    socket.emit('make_move', {
        game_id: gameId,
        from_pos: [fromRow, fromCol],
        to_pos: [toRow, toCol],
        player_id: user.id
    });
}

// Обновление доски
function updateBoard(boardData) {
    board = boardData;
    
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const square = getSquare(row, col);
            const piece = boardData[row][col];
            
            // Очищаем клетку
            square.innerHTML = '';
            square.className = `chess-square ${(row + col) % 2 === 0 ? 'white' : 'black'}`;
            
            // Добавляем фигуру, если есть
            if (piece) {
                const pieceElement = document.createElement('div');
                pieceElement.className = `chess-piece ${piece.color}`;
                pieceElement.textContent = piece.symbol;
                pieceElement.title = `${piece.color} ${piece.type}`;
                square.appendChild(pieceElement);
            }
        }
    }
}

// Получение элемента клетки
function getSquare(row, col) {
    return document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
}

// Обновление статуса игры
function updateGameStatus(status) {
    const statusElement = document.getElementById('gameStatus');
    if (statusElement) {
        statusElement.textContent = status;
    }
}

// Обновление статуса игроков
function updatePlayerStatus() {
    const whiteStatus = document.getElementById('whiteStatus');
    const blackStatus = document.getElementById('blackStatus');
    
    if (whiteStatus && blackStatus) {
        if (playerColor === 'white') {
            whiteStatus.textContent = 'Вы';
            blackStatus.textContent = 'Противник';
        } else {
            whiteStatus.textContent = 'Противник';
            blackStatus.textContent = 'Вы';
        }
    }
}

// Обновление заголовка игры
function updateGameTitle() {
    const titleElement = document.getElementById('gameTitle');
    if (titleElement) {
        const gameName = gameType === 'chess' ? '♔ Шахматы ♛' : '⚪ Шашки ⚫';
        titleElement.textContent = gameName;
    }
}

// Добавление хода в историю
function addMoveToHistory(data) {
    const historyElement = document.getElementById('moveHistory');
    if (historyElement) {
        const moveItem = document.createElement('div');
        moveItem.className = 'history-item';
        
        const fromPos = data.from_pos;
        const toPos = data.to_pos;
        const moveNumber = Math.floor(moveHistory.length / 2) + 1;
        
        if (moveHistory.length % 2 === 0) {
            // Ход белых
            moveItem.textContent = `${moveNumber}. ${getPositionNotation(fromPos)}-${getPositionNotation(toPos)}`;
        } else {
            // Ход черных
            const lastItem = historyElement.lastElementChild;
            if (lastItem) {
                lastItem.textContent += ` ${getPositionNotation(fromPos)}-${getPositionNotation(toPos)}`;
            }
        }
        
        if (moveHistory.length % 2 === 0) {
            historyElement.appendChild(moveItem);
        }
        
        moveHistory.push(data);
        
        // Прокручиваем к последнему ходу
        historyElement.scrollTop = historyElement.scrollHeight;
    }
}

// Получение нотации позиции
function getPositionNotation(pos) {
    const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
    const ranks = ['8', '7', '6', '5', '4', '3', '2', '1'];
    return files[pos[1]] + ranks[pos[0]];
}

// Показать окончание игры
function showGameOver(winner) {
    const modal = document.getElementById('gameOverModal');
    const title = document.getElementById('gameOverTitle');
    const message = document.getElementById('gameOverMessage');
    
    if (winner) {
        const winnerText = winner === playerColor ? 'Поздравляем! Вы победили! 🎉' : 'Вы проиграли 😔';
        title.textContent = 'Игра окончена';
        message.textContent = winnerText;
    } else {
        title.textContent = 'Ничья';
        message.textContent = 'Игра завершилась вничью 🤝';
    }
    
    modal.classList.remove('hidden');
    
    // В Telegram показываем уведомление
    if (isTelegramApp && telegramWebApp.showAlert) {
        telegramWebApp.showAlert(message.textContent);
    }
}

// Показать ошибку
function showError(message) {
    // В Telegram показываем ошибку
    if (isTelegramApp && telegramWebApp.showAlert) {
        telegramWebApp.showAlert('Ошибка: ' + message);
    } else {
        // Обычное уведомление для браузера
        alert('Ошибка: ' + message);
    }
}

// Настройка обработчиков событий
function setupEventListeners() {
    // Кнопка новой игры
    const newGameBtn = document.getElementById('newGameBtn');
    if (newGameBtn) {
        newGameBtn.addEventListener('click', function() {
            if (isTelegramApp) {
                telegramWebApp.close();
            } else {
                window.location.href = '/';
            }
        });
    }
    
    // Кнопка возврата в меню
    const backToMenuBtn = document.getElementById('backToMenuBtn');
    if (backToMenuBtn) {
        backToMenuBtn.addEventListener('click', function() {
            if (isTelegramApp) {
                telegramWebApp.close();
            } else {
                window.location.href = '/';
            }
        });
    }
    
    // Кнопки в модальном окне
    const playAgainBtn = document.getElementById('playAgainBtn');
    if (playAgainBtn) {
        playAgainBtn.addEventListener('click', function() {
            document.getElementById('gameOverModal').classList.add('hidden');
            if (isTelegramApp) {
                telegramWebApp.close();
            } else {
                window.location.href = '/';
            }
        });
    }
    
    const backToMenuBtn2 = document.getElementById('backToMenuBtn2');
    if (backToMenuBtn2) {
        backToMenuBtn2.addEventListener('click', function() {
            document.getElementById('gameOverModal').classList.add('hidden');
            if (isTelegramApp) {
                telegramWebApp.close();
            } else {
                window.location.href = '/';
            }
        });
    }
}

// Добавляем CSS стили для Telegram Web App
const style = document.createElement('style');
style.textContent = `
    /* Telegram Web App стили */
    :root {
        --tg-theme-bg-color: #ffffff;
        --tg-theme-text-color: #000000;
        --tg-theme-button-color: #2481cc;
        --tg-theme-button-text-color: #ffffff;
        --tg-theme-secondary-bg-color: #f1f1f1;
    }
    
    body {
        background-color: var(--tg-theme-bg-color);
        color: var(--tg-theme-text-color);
    }
    
    .btn {
        background-color: var(--tg-theme-button-color);
        color: var(--tg-theme-button-text-color);
    }
    
    .game-sidebar {
        background-color: var(--tg-theme-secondary-bg-color);
    }
    
    /* Адаптивность для мобильных устройств */
    @media (max-width: 768px) {
        .game-main {
            flex-direction: column;
        }
        
        .game-sidebar {
            order: -1;
            margin-bottom: 20px;
        }
        
        .chess-board {
            max-width: 100%;
            height: auto;
        }
    }
`;
document.head.appendChild(style); 

// Функция для игры с компьютером
function showComputerGame() {
    console.log('Запуск игры с компьютером');
    
    // Устанавливаем параметры игры
    playerColor = 'white'; // Игрок всегда играет белыми
    gameType = GAME_TYPE;
    
    // Создаем начальную расстановку шахмат
    const initialBoard = createInitialChessBoard();
    updateBoard(initialBoard);
    
    // Обновляем UI
    updateGameStatus('Ваш ход (белые)');
    updatePlayerStatus();
    updateGameTitle();
    
    // Показываем уведомление
    if (isTelegramApp && telegramWebApp.showAlert) {
        telegramWebApp.showAlert('Игра с компьютером началась! Вы играете белыми.');
    }
    
    // Показываем главную кнопку
    showMainButton();
    
    // Добавляем обработчик для ходов компьютера
    setupComputerGame();
}

// Настройка игры с компьютером
function setupComputerGame() {
    // Переопределяем обработку кликов для игры с компьютером
    const squares = document.querySelectorAll('.chess-square');
    squares.forEach(square => {
        square.addEventListener('click', function() {
            if (isComputerTurn) {
                // Если ход компьютера, игнорируем клик
                return;
            }
            
            const row = parseInt(this.dataset.row);
            const col = parseInt(this.dataset.col);
            handleComputerGameClick(row, col);
        });
    });
}

// Обработка кликов в игре с компьютером
function handleComputerGameClick(row, col) {
    const square = getSquare(row, col);
    const piece = board[row][col];
    
    if (selectedSquare) {
        // Если уже выбрана клетка, пытаемся сделать ход
        const fromRow = parseInt(selectedSquare.dataset.row);
        const fromCol = parseInt(selectedSquare.dataset.col);
        
        if (fromRow === row && fromCol === col) {
            // Кликнули на ту же клетку - отменяем выбор
            clearSelection();
        } else {
            // Пытаемся сделать ход
            if (makeComputerMove(fromRow, fromCol, row, col)) {
                // Ход успешен, теперь ход компьютера
                setTimeout(() => {
                    makeComputerMove();
                }, 1000);
            }
        }
    } else {
        // Выбираем клетку
        if (piece && piece.color === 'white') {
            selectSquare(row, col);
        }
    }
}

// Выполнение хода в игре с компьютером
function makeComputerMove(fromRow, fromCol, toRow, toCol) {
    if (fromRow !== undefined && fromCol !== undefined && toRow !== undefined && toCol !== undefined) {
        // Ход игрока
        const piece = board[fromRow][fromCol];
        if (!piece || piece.color !== 'white') {
            return false;
        }
        
        // Простая проверка хода (можно улучшить)
        if (isValidMove(piece, fromRow, fromCol, toRow, toCol)) {
            // Выполняем ход
            board[toRow][toCol] = piece;
            board[fromRow][fromCol] = null;
            updateBoard(board);
            addMoveToHistory({
                from_pos: [fromRow, fromCol],
                to_pos: [toRow, toCol],
                piece: piece
            });
            clearSelection();
            
            // Передаем ход компьютеру
            isComputerTurn = true;
            updateGameStatus('Ход компьютера (черные)...');
            
            return true;
        }
        return false;
    } else {
        // Ход компьютера
        makeComputerMove();
    }
}

// Простая логика хода компьютера
function makeComputerMove() {
    // Находим все черные фигуры
    const blackPieces = [];
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const piece = board[row][col];
            if (piece && piece.color === 'black') {
                blackPieces.push({row, col, piece});
            }
        }
    }
    
    if (blackPieces.length > 0) {
        // Выбираем случайную фигуру
        const randomPiece = blackPieces[Math.floor(Math.random() * blackPieces.length)];
        
        // Находим возможные ходы для этой фигуры
        const possibleMoves = getPossibleMoves(randomPiece.piece, randomPiece.row, randomPiece.col);
        
        if (possibleMoves.length > 0) {
            // Выбираем случайный ход
            const randomMove = possibleMoves[Math.floor(Math.random() * possibleMoves.length)];
            
            // Выполняем ход
            board[randomMove.row][randomMove.col] = randomPiece.piece;
            board[randomPiece.row][randomPiece.col] = null;
            updateBoard(board);
            addMoveToHistory({
                from_pos: [randomPiece.row, randomPiece.col],
                to_pos: [randomMove.row, randomMove.col],
                piece: randomPiece.piece
            });
            
            // Передаем ход игроку
            isComputerTurn = false;
            updateGameStatus('Ваш ход (белые)');
        }
    }
}

// Простая проверка валидности хода
function isValidMove(piece, fromRow, fromCol, toRow, toCol) {
    // Базовая проверка - фигура не может ходить на клетку с фигурой того же цвета
    const targetPiece = board[toRow][toCol];
    if (targetPiece && targetPiece.color === piece.color) {
        return false;
    }
    
    // Простые правила для пешки
    if (piece.type === 'pawn') {
        if (piece.color === 'white') {
            // Белая пешка ходит вперед
            if (fromCol === toCol && toRow === fromRow - 1 && !targetPiece) {
                return true;
            }
            // Первый ход пешки может быть на 2 клетки
            if (fromRow === 6 && fromCol === toCol && toRow === 4 && !targetPiece && !board[5][fromCol]) {
                return true;
            }
            // Взятие по диагонали
            if (Math.abs(fromCol - toCol) === 1 && toRow === fromRow - 1 && targetPiece) {
                return true;
            }
        }
    }
    
    // Для других фигур пока разрешаем любые ходы
    return true;
}

// Получение возможных ходов для фигуры
function getPossibleMoves(piece, row, col) {
    const moves = [];
    
    // Простая логика для пешки
    if (piece.type === 'pawn') {
        if (piece.color === 'black') {
            // Черная пешка ходит вниз
            if (row < 7 && !board[row + 1][col]) {
                moves.push({row: row + 1, col: col});
            }
            // Первый ход пешки может быть на 2 клетки
            if (row === 1 && !board[2][col] && !board[3][col]) {
                moves.push({row: 3, col: col});
            }
            // Взятие по диагонали
            if (row < 7 && col > 0 && board[row + 1][col - 1] && board[row + 1][col - 1].color === 'white') {
                moves.push({row: row + 1, col: col - 1});
            }
            if (row < 7 && col < 7 && board[row + 1][col + 1] && board[row + 1][col + 1].color === 'white') {
                moves.push({row: row + 1, col: col + 1});
            }
        }
    }
    
    return moves;
} 