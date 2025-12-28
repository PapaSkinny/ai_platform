import streamlit as st
import os
import shutil
from src.rag_engine import save_uploaded_file, create_vector_db, load_existing_db
from src.agents.rag_agent import get_rag_agent, set_vector_store

def show():
    st.header("📚 База Знаний (RAG)")
    st.caption("Задайте вопрос по вашим документам (PDF/TXT).")

    # --- ЛОГИКА ВОССТАНОВЛЕНИЯ СОСТОЯНИЯ ---
    # Это ключевой момент! При перезагрузке страницы (когда вы пишете вопрос),
    # Streamlit забывает глобальные переменные. Нам нужно восстановить базу.
    if "rag_db_path" in st.session_state:
        db_path = st.session_state.rag_db_path
        # Тихая загрузка существующей базы
        if os.path.exists(db_path):
            vector_store = load_existing_db(db_path)
            set_vector_store(vector_store)
            # print(f"[DEBUG] База восстановлена из {db_path}")

    # --- СЕКЦИЯ ЗАГРУЗКИ ---
    with st.expander("📂 Управление документом", expanded=True):
        uploaded_file = st.file_uploader("Перетащите файл сюда", type=["pdf", "txt"])
        
        if uploaded_file:
            if st.button("🚀 Обработать файл", type="primary"):
                with st.status("⚙️ Создаю базу знаний...", expanded=True) as status:
                    try:
                        # 1. Сохраняем и векторизуем (в новую уникальную папку)
                        st.write("Обработка файла...")
                        file_path = save_uploaded_file(uploaded_file)
                        
                        # create_vector_db теперь возвращает ДВА значения
                        vector_store, db_path = create_vector_db(file_path)
                        
                        # 2. Передаем агенту
                        set_vector_store(vector_store)
                        
                        # 3. ЗАПОМИНАЕМ ПУТЬ В СЕССИИ
                        st.session_state.rag_db_path = db_path
                        st.session_state.current_rag_file = uploaded_file.name
                        
                        status.update(label="✅ Готово! База подключена.", state="complete", expanded=False)
                        
                    except Exception as e:
                        status.update(label="❌ Ошибка", state="error")
                        st.error(f"Ошибка обработки: {e}")

    # Индикатор
    if "current_rag_file" in st.session_state:
        st.success(f"🟢 Активный документ: **{st.session_state.current_rag_file}**")
    else:
        st.warning("Загрузите файл, чтобы начать.")

    # --- ЧАТ ---
    st.divider()
    
    if "rag_msgs" not in st.session_state:
        st.session_state.rag_msgs = []

    for msg in st.session_state.rag_msgs:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    query = st.chat_input("Например: 'Какие условия возврата?'")
    
    if query:
        # Проверяем, подключена ли база (путь есть в сессии)
        if "rag_db_path" not in st.session_state:
            st.error("⛔ Сначала загрузите и обработайте файл!")
        else:
            st.session_state.rag_msgs.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.write(query)

            with st.chat_message("assistant"):
                with st.spinner("Ищу ответ..."):
                    try:
                        agent = get_rag_agent()
                        response = agent.invoke({"input": query})
                        output = response["output"]
                        
                        st.write(output)
                        st.session_state.rag_msgs.append({"role": "assistant", "content": output})
                    except Exception as e:
                        st.error(f"Ошибка агента: {e}")

if __name__ == "__main__":
    show()