#!/usr/bin/env python3
"""
Простой тест Flask приложения
"""

from app import app

if __name__ == '__main__':
    print("🚀 Запуск простого Flask приложения...")
    app.run(debug=True, host='0.0.0.0', port=5000) 