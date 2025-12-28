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

