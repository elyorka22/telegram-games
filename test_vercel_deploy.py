#!/usr/bin/env python3
"""
Тестовый скрипт для проверки endpoints перед деплоем на Vercel
"""

import urllib.request
import urllib.error
import json
import sys

def test_endpoint(url, name):
    """Тестирует endpoint и выводит результат"""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"✅ {name}: {response.status}")
            if response.status == 200:
                data = response.read().decode('utf-8')
                try:
                    json_data = json.loads(data)
                    print(f"   Response: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
                except:
                    print(f"   Response: {data[:100]}...")
            else:
                print(f"   Error: {data}")
    except urllib.error.HTTPError as e:
        print(f"❌ {name}: HTTP Error {e.code} - {e.reason}")
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
    
    print()

def main():
    """Основная функция тестирования"""
    base_url = "http://localhost:5000"
    
    print("🚀 Тестирование endpoints для деплоя на Vercel")
    print("=" * 50)
    
    # Тестируем основные endpoints
    test_endpoint(f"{base_url}/", "Главная страница")
    test_endpoint(f"{base_url}/health", "Health check")
    test_endpoint(f"{base_url}/test", "Test endpoint")
    
    # Тестируем страницы
    test_endpoint(f"{base_url}/game", "Game page")
    
    print("=" * 50)
    print("✅ Тестирование завершено!")
    print("\n📋 Следующие шаги для деплоя:")
    print("1. Установите Vercel CLI: npm i -g vercel")
    print("2. Войдите в аккаунт: vercel login")
    print("3. Задеплойте: vercel")
    print("4. Для продакшн: vercel --prod")
    print("\n📁 Файлы конфигурации созданы:")
    print("- vercel.json - конфигурация Vercel")
    print("- requirements.txt - Python зависимости")
    print("- runtime.txt - версия Python")
    print("- .vercelignore - исключения для деплоя")
    print("- api/index.py - API endpoints")
    print("- package.json - метаданные проекта")

if __name__ == "__main__":
    main() 