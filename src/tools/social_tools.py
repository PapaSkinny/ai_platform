import os
import requests
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

@tool("post_to_telegram")
def telegram_poster_tool(message: str, image_path: str = None):
    """
    Публикует пост в Telegram.
    
    ВАЖНО:
    - Если ты хочешь отправить фото, переменная image_path ОБЯЗАНА содержать путь к СУЩЕСТВУЮЩЕМУ файлу.
    - Сначала вызови инструмент генерации, получи от него имя файла, и только потом передавай его сюда.
    - Не выдумывай имена файлов!
    """
    if not BOT_TOKEN or not CHAT_ID:
        return "Ошибка: Не настроены TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID."

    try:
        # Логика отправки
        if image_path and image_path.lower() != "none" and len(image_path) > 4:
            # СТРОГАЯ ПРОВЕРКА: Если путь передан, но файла нет — возвращаем ошибку!
            if not os.path.exists(image_path):
                return f"ОШИБКА: Файл '{image_path}' не найден на диске. Ты забыл вызвать инструмент 'generate_image' или выдумал имя файла. Сначала сгенерируй картинку!"
            
            # Если файл есть — отправляем
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            with open(image_path, "rb") as f:
                files = {"photo": f}
                data = {"chat_id": CHAT_ID, "caption": message, "parse_mode": "Markdown"}
                response = requests.post(url, files=files, data=data)
        else:
            # Только текст
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {"chat_id": CHAT_ID, "text": message}
            response = requests.post(url, data=data)

        if response.status_code == 200:
            return "Успешно опубликовано в Telegram!"
        else:
            return f"Ошибка Telegram API: {response.text}"

    except Exception as e:
        return f"Критическая ошибка публикации: {e}"
