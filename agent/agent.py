import autogen
import json
import requests
from ollama_adapter import check_ollama_connection

# Проверяем подключение перед запуском
if not check_ollama_connection():
    print("\n❌ Ollama не запущена. Выполните в отдельном терминале WSL2:")
    print("OLLAMA_ORIGINS=\"http://localhost:*\" ollama serve")
    exit(1)

# Получаем список доступных моделей
def get_available_models():
    try:
        response = requests.get(
            "http://localhost:11434/api/tags",
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            print("✅ Доступные модели:", models)
            return models
        else:
            print(f"⚠️ Ошибка получения списка моделей: {response.status_code}")
            return []
    except Exception as e:
        print(f"⚠️ Ошибка при запросе списка моделей: {e}")
        return []

# Получаем полное имя модели
available_models = get_available_models()
model_name = "mistral:7b-instruct-v0.2-q4_0"  # Имя по умолчанию

# Ищем подходящую модель в списке
for model in available_models:
    if "mistral" in model.lower() and ("q4" in model or "instruct" in model):
        model_name = model
        print(f"✅ Выбрана модель: {model_name}")
        break

# Создаем config_list с правильным именем модели
config_list = [
    {
        "model": model_name,
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "temperature": 0.1,
        "max_tokens": 500
    }
]

# Создаем агентов
forecast_agent = autogen.AssistantAgent(
    name="ForecastAgent",
    llm_config={"config_list": config_list},
    system_message="""
    Ты — аналитик данных. Прогнозируй спрос на товар на основе исторических данных.
    Правила:
    1. Используй только предоставленные данные
    2. Ответь только в формате JSON: {"forecast": число}
    3. Не добавляй комментарии
    4. Заверши ответ словом TERMINATE
    """
)

user_proxy = autogen.UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config=False,
)

# Тестовые данные
input_data = {
    "product": "Кофемашина",
    "historical_sales": [120, 150, 130, 160],
    "season": "winter"
}

task = f"""
Сделай прогноз спроса для товара:
- Название: {input_data['product']}
- Продажи за последние 4 месяца: {input_data['historical_sales']}
- Сезон: {input_data['season']}
"""

print("="*50)
print("🚀 Запускаем ИИ-агента для прогнозирования...")
print("="*50)

# Запускаем диалог
chat_result = user_proxy.initiate_chat(
    forecast_agent,
    message=task
)

# Извлекаем результат
response = user_proxy.last_message()["content"]
print("\n" + "="*50)
print("📊 Результат прогноза:")
print("="*50)
print(response)

# Пытаемся распарсить JSON
try:
    # Извлекаем JSON из ответа
    json_str = response.split("TERMINATE")[0].strip()
    forecast_data = json.loads(json_str)
    print(f"\n✅ Прогноз: {forecast_data['forecast']} единиц")
except json.JSONDecodeError as e:
    print(f"\n❌ Ошибка парсинга JSON: {e}")
    print("Необработанный ответ:", response)
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    print("Ответ агента:", response)