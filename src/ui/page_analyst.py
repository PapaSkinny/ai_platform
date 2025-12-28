import streamlit as st
import pandas as pd
import os
import time
import re
import json # Добавили json для парсинга
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from src.utils import get_llm
from src.agents.analyst_agent import AnalystManager
from src.tools.search_tools import tavily_search_tool 

def show():
    st.markdown("""
        <h1 style='text-align: center; color: #00ADB5;'>
            📊 AI Business Analyst
        </h1>
        <p style='text-align: center; color: #888;'>
            Анализ внутренней отчетности и внешнего рынка в реальном времени
        </p>
        <hr>
    """, unsafe_allow_html=True)
    # Используем табы, чтобы разделить загрузку и чат
    tab1, tab2 = st.tabs(["📂 Данные", "💬 Чат с Аналитиком"])
    
    st.header("📊 Умная Аналитика + Рынок")
    st.caption("Анализ файла и поиск в интернете с реальными источниками.")
    

    # 1. Загрузка файла
    with tab1:
        uploaded_file = st.file_uploader("Файл продаж", type=["csv", "xlsx"])
        tools= [tavily_search_tool]
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
            except Exception as e:
                st.error(f"Не удалось открыть файл: {e}")
                return

            with st.expander("👀 Просмотр таблицы"):
                st.dataframe(df.head())

            # 2. Сборка инструментов
            manager = AnalystManager(df)
            data_tool = manager.get_tool()
            tools = [data_tool, tavily_search_tool]
        llm = get_llm()
        # 3. Промпт
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
            "Ты — Главный Бизнес-Аналитик. \n"
            "1. Используй 'analyze_file_data' для анализа данных пользователя.\n"
            "2. Используй 'web_search' для поиска в интернете  .\n"
            "3. Сравнивай цифры и давай советы.\n"
            "ВАЖНО: Никогда не упоминай названия файлов (plot.png) и технические теги источников в тексте."
            ),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        agent = AgentExecutor(
            agent=create_tool_calling_agent(llm,tools, prompt), 
            tools=tools, 
            verbose=True,
            return_intermediate_steps=True # Обязательно True, чтобы видеть работу инструментов
        )
    with tab2:
            # 4. История
        if "analyst_msgs" not in st.session_state:
            st.session_state.analyst_msgs = []

        for msg in st.session_state.analyst_msgs:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if msg.get("has_plot") and os.path.exists("plot.png"):
                    st.image("plot.png", caption="Архивный график")
                
                if msg.get("sources"):
                    with st.expander("📚 Использованные источники"):
                        for source in msg["sources"]:
                            st.markdown(f"🔗 [{source['url']}]({source['url']})")

        # 5. Ввод
        query = st.chat_input("Пример: 'Сравни мои цены на iPhone с ценами на Авито'")
        
        if query:
            st.session_state.analyst_msgs.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.write(query)

            with st.chat_message("assistant"):
                if os.path.exists("plot.png"):
                    os.remove("plot.png")

                with st.spinner("Анализирую данные..."):
                    try:
                        response = agent.invoke({"input": query})
                        raw_output = response["output"]
                        
                        # --- ОЧИСТКА ТЕКСТА ---
                        clean_text = re.sub(r'\[sources=\[.*?\]\]', '', raw_output)
                        clean_text = re.sub(r'\[sources=.*?\]', '', clean_text)
                        clean_text = clean_text.replace("plot.png", "").replace("chart.json", "").strip()
                        
                        st.write(clean_text)
                        
                        # --- МОЩНОЕ ИЗВЛЕЧЕНИЕ ССЫЛОК ---
                        sources_found = []
                        seen_urls = set() # Чтобы не было дублей
                        
                        # Проходимся по всем шагам агента
                        for action, observation in response["intermediate_steps"]:
                            # Если инструмент был поисковым (имя обычно web_search)
                            if action.tool == "web_search":
                                
                                # ВАРИАНТ 1: Это список словарей (идеальный случай)
                                if isinstance(observation, list):
                                    for item in observation:
                                        url = item.get('url')
                                        if url and url not in seen_urls:
                                            sources_found.append({'url': url})
                                            seen_urls.add(url)
                                
                                # ВАРИАНТ 2: Это строка (JSON или просто текст)
                                elif isinstance(observation, str):
                                    # Попытка 1: Найти URL через Regex (самое надежное)
                                    # Ищем все, что начинается на http/https
                                    urls = re.findall(r'(https?://[^\s\'"<>\]]+)', observation)
                                    for url in urls:
                                        # Чистим от лишних знаков в конце, которые мог захватить regex
                                        clean_url = url.rstrip(",').]\"")
                                        if clean_url not in seen_urls:
                                            sources_found.append({'url': clean_url})
                                            seen_urls.add(clean_url)

                        # --- ГРАФИК ---
                        has_plot = False
                        time.sleep(1) 
                        if os.path.exists("plot.png"):
                            st.image("plot.png", caption="Визуализация")
                            has_plot = True

                        # --- ВЫВОД ССЫЛОК ---
                        if sources_found:
                            with st.expander("📚 Использованные источники (Кликабельно)", expanded=True):
                                for source in sources_found:
                                    st.markdown(f"🔗 [{source['url']}]({source['url']})")
                        else:
                            # Для отладки (если вдруг ссылок нет, увидим почему)
                            # st.caption("Источники не найдены в ответе инструмента.") 
                            pass

                        # Сохраняем
                        st.session_state.analyst_msgs.append({
                            "role": "assistant",
                            "content": clean_text,
                            "has_plot": has_plot,
                            "sources": sources_found
                        })
                        
                    except Exception as e:
                        st.error(f"Ошибка: {e}")

if __name__ == "__main__":
    show()
