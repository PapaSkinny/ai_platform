import os
from langchain_tavily import TavilySearch
from langchain_core.tools import tool

# --- 1. Текстовый поиск (Для Аналитика) ---
@tool("web_search")
def tavily_search_tool(query: str):
    """
    Выполняет поиск в интернете (Google/Bing через Tavily).
    Используй это для поиска цен конкурентов, трендов рынка, новостей и аналитики.
    Возвращает текст с результатами.
    """
    # max_results=5, чтобы получить достаточно данных для анализа
    search = TavilySearch(max_results=5)
    return search.invoke({"query": query})
    
# --- 2. Поиск картинок (Для Контент-мейкера) ---
@tool("image_search")
def image_finder_tool(query: str):
    """
    Ищет URL картинок. Используй для поиска референсов и фото товаров.
    """
    search = TavilySearch(
        max_results=5, 
        include_images=True,
        search_depth="advanced"
    )
    results = search.invoke({"query": query})
    
    # Фильтруем, оставляем картинки
    images = [res.get('image') for res in results if res.get('image')]
    return f"Найденные изображения: {images}"


