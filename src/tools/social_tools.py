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

    Вход:
    - message: текст сообщения.
    - image_path: опциональный путь к изображению.
    """
    if not BOT_TOKEN or not CHAT_ID:
        return "Ошибка: Не настроены TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID."

    try:
        # Только текстовое сообщение
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}
        response = requests.post(url, data=data)

        if response.status_code == 200:
            return "Успешно опубликовано в Telegram!"
        else:
            return f"Ошибка Telegram API: {response.text}"
    except Exception as e:
        return f"Критическая ошибка публикации: {e}"
