// JavaScript для главной страницы онлайн игр

let socket = null;
let isConnected = false;
let telegramWebApp = null;
let isTelegramApp = false;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initializeTelegramWebApp();
    initializeSocket();
    setupEventListeners();
    setupTelegramUI();
});

// Инициализация Telegram Web App
function initializeTelegramWebApp() {
    // Проверяем, запущено ли приложение в Telegram
    if (window.Telegram && window.Telegram.WebApp) {
        telegramWebApp = window.Telegram.WebApp;
        isTelegramApp = true;
        
        console.log('Telegram Web App инициализирован');
        
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
        
        // Проверяем параметры запуска
        const urlParams = new URLSearchParams(window.location.search);
        const gameType = urlParams.get('game');
        if (gameType) {
            // Автоматически запускаем игру, если указан тип
            setTimeout(() => {
                findGame(gameType);
            }, 1000);
        }
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
    
    // Скрываем заголовок в Telegram (он уже есть в Telegram UI)
    const header = document.querySelector('.header');
    if (header) {
        header.style.display = 'none';
    }
    
    // Настраиваем кнопки для Telegram
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.style.backgroundColor = telegramWebApp.themeParams?.button_color || '#2481cc';
        button.style.color = telegramWebApp.themeParams?.button_text_color || '#ffffff';
    });
}

// Инициализация WebSocket соединения
function initializeSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Подключен к серверу');
        isConnected = true;
        updateConnectionStatus('Подключен');
    });
    
    socket.on('disconnect', function() {
        console.log('Отключен от сервера');
        isConnected = false;
        updateConnectionStatus('Отключен');
    });
    
    socket.on('connected', function(data) {
        console.log('Получен ID сессии:', data.sid);
    });
    
    socket.on('waiting_for_opponent', function(data) {
        showStatus(data.message, true);
        console.log(data.message);
        
        // В Telegram показываем уведомление
        if (isTelegramApp && telegramWebApp.showAlert) {
            telegramWebApp.showAlert(data.message);
        }
    });
    
    socket.on('game_started', function(data) {
        console.log('Игра началась:', data);
        hideStatus();
        
        // В Telegram показываем уведомление
        if (isTelegramApp && telegramWebApp.showAlert) {
            telegramWebApp.showAlert('Игра началась! Удачной игры! 🎮');
        }
        
        // Перенаправляем на страницу игры
        window.location.href = `/game/${data.game_id}`;
    });
    
    socket.on('error', function(data) {
        showError(data.message);
        
        // В Telegram показываем ошибку
        if (isTelegramApp && telegramWebApp.showAlert) {
            telegramWebApp.showAlert('Ошибка: ' + data.message);
        }
    });
}

// Настройка обработчиков событий
function setupEventListeners() {
    // Кнопка поиска игры в шахматы
    const findChessGameBtn = document.getElementById('findChessGameBtn');
    if (findChessGameBtn) {
        findChessGameBtn.addEventListener('click', () => findGame('chess'));
    }
    
    // Кнопка поиска игры в шашки
    const findCheckersGameBtn = document.getElementById('findCheckersGameBtn');
    if (findCheckersGameBtn) {
        findCheckersGameBtn.addEventListener('click', () => findGame('checkers'));
    }
    
    // Закрытие модального окна
    const closeBtn = document.querySelector('.close');
    if (closeBtn) {
        closeBtn.addEventListener('click', hideRules);
    }
    
    // Закрытие модального окна по клику вне его
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('rulesModal');
        if (event.target === modal) {
            hideRules();
        }
    });
    
    // Обработка нажатия Escape для закрытия модального окна
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            hideRules();
        }
    });
}

// Поиск игры
function findGame(gameType) {
    if (!isConnected) {
        showError('Нет подключения к серверу');
        return;
    }
    
    const gameName = gameType === 'chess' ? 'шахматы' : 'шашки';
    const buttonId = gameType === 'chess' ? 'findChessGameBtn' : 'findCheckersGameBtn';
    const button = document.getElementById(buttonId);
    
    if (!button) {
        showError('Кнопка не найдена');
        return;
    }
    
    button.disabled = true;
    button.textContent = `Поиск игры в ${gameName}...`;
    
    showStatus(`Поиск противника для игры в ${gameName}...`, true);
    
    // В Telegram показываем прогресс
    if (isTelegramApp && telegramWebApp.showProgress) {
        telegramWebApp.showProgress();
    }
    
    socket.emit('find_game', { game_type: gameType });
}

// Показать правила
function showRules() {
    const modal = document.getElementById('rulesModal');
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden'; // Запретить прокрутку страницы
}

// Скрыть правила
function hideRules() {
    const modal = document.getElementById('rulesModal');
    modal.classList.add('hidden');
    document.body.style.overflow = 'auto'; // Разрешить прокрутку страницы
}

// Показать статус
function showStatus(message, showSpinner = false) {
    const status = document.getElementById('status');
    const statusText = document.getElementById('statusText');
    const spinner = status.querySelector('.loading-spinner');
    
    statusText.textContent = message;
    status.classList.remove('hidden');
    
    if (showSpinner) {
        spinner.style.display = 'block';
    } else {
        spinner.style.display = 'none';
    }
}

// Скрыть статус
function hideStatus() {
    const status = document.getElementById('status');
    status.classList.add('hidden');
    
    // В Telegram скрываем прогресс
    if (isTelegramApp && telegramWebApp.hideProgress) {
        telegramWebApp.hideProgress();
    }
}

// Показать ошибку
function showError(message) {
    // Создаем временное уведомление об ошибке
    const notification = document.createElement('div');
    notification.className = 'error-notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #ff6b6b;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Удаляем уведомление через 3 секунды
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Обновить статус подключения
function updateConnectionStatus(status) {
    console.log('Статус подключения:', status);
    // Можно добавить визуальную индикацию статуса подключения
}

// Добавляем CSS анимации для уведомлений
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
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
    
    .game-card {
        background-color: var(--tg-theme-secondary-bg-color);
    }
`;
document.head.appendChild(style);

// Обработка отключения страницы
window.addEventListener('beforeunload', function() {
    if (socket) {
        socket.disconnect();
    }
});

// Обработка восстановления соединения
window.addEventListener('online', function() {
    if (socket && !isConnected) {
        socket.connect();
    }
});

window.addEventListener('offline', function() {
    isConnected = false;
    updateConnectionStatus('Нет интернета');
}); 