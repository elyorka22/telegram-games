#!/usr/bin/env python3
"""
Скрипт для проверки готовности проекта к деплою в Railway
"""

import os
import sys
import importlib.util

def check_file_exists(filename, description):
    """Проверка существования файла"""
    if os.path.exists(filename):
        print(f"✅ {description}: {filename}")
        return True
    else:
        print(f"❌ {description}: {filename} - НЕ НАЙДЕН")
        return False

def check_import(module_name, description):
    """Проверка возможности импорта модуля"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except ImportError:
        print(f"❌ {description}: {module_name} - НЕ УСТАНОВЛЕН")
        return False

def check_requirements():
    """Проверка файла requirements.txt"""
    if not check_file_exists('requirements.txt', 'Файл зависимостей'):
        return False
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        # Проверяем наличие основных зависимостей
        essential_deps = [
            'Flask',
            'python-telegram-bot',
            'flask-socketio',
            'python-dotenv'
        ]
        
        missing_deps = []
        for dep in essential_deps:
            if dep.lower() not in requirements.lower():
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"❌ Отсутствуют зависимости: {', '.join(missing_deps)}")
            return False
        else:
            print("✅ Все основные зависимости присутствуют")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка чтения requirements.txt: {e}")
        return False

def check_configuration():
    """Проверка конфигурационных файлов"""
    config_files = [
        ('railway.json', 'Конфигурация Railway'),
        ('Procfile', 'Procfile для Railway'),
        ('runtime.txt', 'Версия Python'),
        ('env.example', 'Пример переменных окружения')
    ]
    
    all_good = True
    for filename, description in config_files:
        if not check_file_exists(filename, description):
            all_good = False
    
    return all_good

def check_main_files():
    """Проверка основных файлов приложения"""
    main_files = [
        ('telegram_bot.py', 'Основной файл Telegram бота'),
        ('app.py', 'Flask приложение'),
        ('chess_game.py', 'Логика шахмат'),
        ('checkers_game.py', 'Логика шашек')
    ]
    
    all_good = True
    for filename, description in main_files:
        if not check_file_exists(filename, description):
            all_good = False
    
    return all_good

def check_templates():
    """Проверка шаблонов"""
    template_files = [
        ('templates/index.html', 'Главная страница'),
        ('templates/game.html', 'Страница игры')
    ]
    
    all_good = True
    for filename, description in template_files:
        if not check_file_exists(filename, description):
            all_good = False
    
    return all_good

def check_static_files():
    """Проверка статических файлов"""
    static_dirs = [
        ('static/css', 'CSS файлы'),
        ('static/js', 'JavaScript файлы')
    ]
    
    all_good = True
    for dirname, description in static_dirs:
        if os.path.exists(dirname) and os.path.isdir(dirname):
            print(f"✅ {description}: {dirname}")
        else:
            print(f"❌ {description}: {dirname} - НЕ НАЙДЕН")
            all_good = False
    
    return all_good

def main():
    """Главная функция проверки"""
    print("🔍 Проверка готовности проекта к деплою в Railway")
    print("=" * 50)
    
    checks = [
        ("Конфигурационные файлы", check_configuration),
        ("Основные файлы приложения", check_main_files),
        ("Зависимости", check_requirements),
        ("Шаблоны", check_templates),
        ("Статические файлы", check_static_files)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 Все проверки пройдены! Проект готов к деплою.")
        print("\n📝 Следующие шаги:")
        print("1. Создайте проект в Railway")
        print("2. Настройте переменные окружения")
        print("3. Подключите Git репозиторий")
        print("4. Задеплойте приложение")
        print("\n📖 Подробные инструкции: DEPLOYMENT.md")
    else:
        print("❌ Обнаружены проблемы. Исправьте их перед деплоем.")
        sys.exit(1)

if __name__ == '__main__':
    main() 