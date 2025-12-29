import streamlit as st
import os

from src.agents.content_agent import get_content_agent


def show():
    st.header("🎨 Контент-Мейкер & Дизайнер")
    st.caption("Генерация изображений и поиск референсов.")

    st.header("🎨 SMM-Автопилот")

    # Настройка автопубликации
    auto_post = st.toggle(
        "🚀 Разрешить автоматическую публикацию в Telegram",
        value=False,
    )

    # --- ИСТОРИЯ ЧАТА ---
    if "content_msgs" not in st.session_state:
        st.session_state.content_msgs = []

    # Вывод истории
    for msg in st.session_state.content_msgs:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- ВВОД ПОЛЬЗОВАТЕЛЯ ---
    query = st.chat_input("Например: 'Нарисуй футуристичный ноутбук на Марсе'")

    if query:
        # 1. Сохраняем и показываем вопрос
        st.session_state.content_msgs.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.write(query)

        # Пока просто сохраняем текстовый ответ-заглушку
        with st.chat_message("assistant"):
            st.markdown("Работаю над генерацией контента...")


# Обязательно для запуска через st.Page
if __name__ == "__main__":
    show()
