import requests
import uuid
from langchain_core.tools import tool


@tool("generate_image")
def generate_image_tool(prompt: str):
    """
    Генерирует изображение через внешний сервис.

    Вход: описание картинки (промпт).
    Выход: путь к сохраненному файлу.
    """
    # TODO: реализовать обращение к сервису генерации
    pass
