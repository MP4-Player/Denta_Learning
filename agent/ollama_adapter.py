import requests
import time

def check_ollama_connection():
    """Проверяет подключение к Ollama API"""
    try:
        # Проверяем базовый эндпоинт
        response = requests.get("http://localhost:11434", timeout=3)
        if response.status_code != 200:
            print(f"Базовый эндпоинт недоступен. Статус: {response.status_code}")
            return False
        
        # Проверяем API-эндпоинт для получения списка моделей
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print(f"API-эндпоинт недоступен. Статус: {response.status_code}")
            return False
            
        print("✅ Ollama API доступен")
        return True
    except Exception as e:
        print(f"⚠️ Ошибка подключения к Ollama: {e}")
        return False