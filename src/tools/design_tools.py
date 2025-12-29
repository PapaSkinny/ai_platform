import requests
import uuid
from langchain_core.tools import tool
import urllib.parse

@tool("generate_image")
def generate_image_tool(prompt: str):
    """
    Генерирует изображение бесплатно через Pollinations AI.
    Вход: описание картинки (промпт) на английском или русском.
    Выход: путь к сохраненному файлу.
    """
    try:
        # 1. Подготавливаем промпт (кодируем пробелы и кириллицу)
        encoded_prompt = urllib.parse.quote(prompt)
        
        # 2. Формируем URL (можно добавить параметры model, width, height)
        # Модели: 'flux', 'turbo'
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=flux&width=1024&height=768&nologo=true"
        
        # 3. Скачиваем картинку
        response = requests.get(image_url)
        
        if response.status_code == 200:
            # Генерируем уникальное имя
            filename = f"generated_image_{uuid.uuid4().hex[:6]}.jpg"
            
            with open(filename, 'wb') as f:
                f.write(response.content)
                
            return f"Изображение успешно сгенерировано и сохранено как: {filename}"
        else:
            return f"Ошибка сервиса генерации: {response.status_code}"
            
    except Exception as e:
        return f"Ошибка при генерации: {e}"
