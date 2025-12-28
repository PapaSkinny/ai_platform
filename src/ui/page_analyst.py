import streamlit as st
import pandas as pd
import os
import time
import re
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from src.utils import get_llm
from src.agents.analyst_agent import AnalystManager
from src.tools.search_tools import tavily_search_tool 

def show():
    st.header("📊 Бизнес-Аналитик")
    st.caption("Анализ внутренней отчетности и внешнего рынка.")

    # --- 1. СЕКЦИЯ ДАННЫХ (В Expander) ---
    # expanded=True, если файл еще не загружен. Если загружен - сворачиваем, чтобы не мешал.
    is_expanded = "analyst_df" not in st.session_state
    
    with st.expander("📂 Загрузка файла и Настройки", expanded=is_expanded):
        uploaded_file = st.file_uploader("Загрузите отчет (CSV/XLSX)", type=["csv", "xlsx"])
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Сохраняем DF в сессию, чтобы не терять при обновлении
                st.session_state.analyst_df = df
                st.success(f"Файл загружен: {len(df)} строк")
                st.dataframe(df.head(10), use_container_width=True)
                
            except Exception as e:
                st.error(f"Не удалось открыть файл: {e}")

    # --- 2. ПОДГОТОВКА АГЕНТА ---
    # Проверяем, есть ли данные в сессии
    if "analyst_df" in st.session_state:
        df = st.session_state.analyst_df
        
        # Сборка инструментов
        manager = AnalystManager(df)
        data_tool = manager.get_tool()
        llm = get_llm()
        tools = [data_tool, tavily_search_tool] 
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "Ты — Главный Бизнес-Аналитик. \n"
             "1. Используй 'analyze_file_data' для внутренних данных.\n"
             "2. Используй 'web_search' для внешних цен.\n"
             "3. Сравнивай цифры и давай советы.\n"
             "ВАЖНО: Никогда не упоминай названия файлов (plot.png) и технические теги источников в тексте."
            ),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        agent = AgentExecutor(
            agent=create_tool_calling_agent(llm, tools, prompt), 
            tools=tools, 
            verbose=True,
            return_intermediate_steps=True 
        )
    else:
        # Если файла нет, агент пока не нужен, но чтобы код не падал ниже
        agent = None

    # --- 3. ИСТОРИЯ ЧАТА ---
    st.divider() # Визуальный разделитель между файлом и чатом
    
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

    # --- 4. ВВОД ВОПРОСА ---
    # Теперь input находится в корне страницы, он будет прибит к низу
    query = st.chat_input("Например: 'Сравни мои цены на iPhone с ценами на Авито'")
    
    if query:
        if agent is None:
            st.error("⛔ Сначала загрузите файл в меню сверху!")
        else:
            st.session_state.analyst_msgs.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.write(query)

            with st.chat_message("assistant"):
                # Чистим старый график
                if os.path.exists("plot.png"):
                    os.remove("plot.png")

                with st.spinner("Анализирую данные..."):
                    try:
                        response = agent.invoke({"input": query})
                        raw_output = response["output"]
                        
                        # --- ОЧИСТКА ---
                        clean_text = re.sub(r'\[sources=\[.*?\]\]', '', raw_output)
                        clean_text = re.sub(r'\[sources=.*?\]', '', clean_text)
                        clean_text = clean_text.replace("plot.png", "").replace("chart.json", "").strip()
                        
                        st.write(clean_text)
                        
                        # --- ССЫЛКИ ---
                        sources_found = []
                        seen_urls = set()
                        
                        for action, observation in response["intermediate_steps"]:
                            if action.tool == "web_search":
                                if isinstance(observation, list):
                                    for item in observation:
                                        url = item.get('url')
                                        if url and url not in seen_urls:
                                            sources_found.append({'url': url})
                                            seen_urls.add(url)
                                elif isinstance(observation, str):
                                    urls = re.findall(r'(https?://[^\s\'"<>\]]+)', observation)
                                    for url in urls:
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
                            with st.expander("📚 Источники (Кликабельно)", expanded=True):
                                for source in sources_found:
                                    st.markdown(f"🔗 [{source['url']}]({source['url']})")

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
