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
    # TODO: реализовать отправку сообщения в Telegram
    pass
