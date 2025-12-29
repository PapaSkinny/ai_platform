import streamlit as st
import os
import re  # <--- Добавили для поиска имени файла в тексте
import time
from src.agents.content_agent import get_content_agent

def show():
    st.header("🎨 Контент-Мейкер & Дизайнер")
    st.caption("Генерация изображений и поиск референсов.")
    st.header("🎨 SMM-Автопилот")
    
    # Добавляем настройку в сайдбар или прямо над чатом
    auto_post = st.toggle("🚀 Разрешить автоматическую публикацию в Telegram", value=False)

    # --- ИСТОРИЯ ЧАТА ---
    if "content_msgs" not in st.session_state:
        st.session_state.content_msgs = []

    # Вывод истории
    for msg in st.session_state.content_msgs:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # Если к сообщению прикреплена картинка, показываем её
            if msg.get("image_path") and os.path.exists(msg["image_path"]):
                st.image(msg["image_path"], caption="Сгенерировано AI")

    # --- ВВОД ПОЛЬЗОВАТЕЛЯ ---
    query = st.chat_input("Например: 'Нарисуй футуристичный ноутбук на Марсе'")
    
    if query:
        # 1. Показываем вопрос
        st.session_state.content_msgs.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.write(query)

        if auto_post:
             final_query = query + " (После генерации ОБЯЗАТЕЛЬНО опубликуй пост в Telegram)"
        else:
             final_query = query + " (Только сгенерируй текст и фото, НЕ публикуй в Telegram, просто покажи результат)"
             
        # 2. Ответ Агента
        with st.chat_message("assistant"):
            with st.spinner("Креативлю..."):
                try:
                    agent = get_content_agent()
                    response = agent.invoke({"input": final_query})
                    output = response["output"]
                    
                    st.markdown(output)
                    
                    # --- ГЛАВНОЕ ИСПРАВЛЕНИЕ ТУТ ---
                    
                    image_path = None
                    
                    # 1. Ищем имя файла в тексте ответа агента
                    # Агент обычно пишет: "... сохранено как: generated_image_xxxx.jpg"
                    # Мы ищем паттерн: generated_image_ + любые символы + .jpg
                    match = re.search(r"(generated_image_[a-zA-Z0-9]+\.jpg)", output)
                    
                    if match:
                        found_filename = match.group(1)
                        
                        # Даем системе время на запись файла (на всякий случай)
                        time.sleep(0.5)
                        
                        if os.path.exists(found_filename):
                            image_path = found_filename
                            st.image(image_path, caption="Результат генерации")
                        else:
                            st.warning(f"Агент сказал, что создал файл '{found_filename}', но я не могу его найти.")
                    
                    # Сохраняем в историю
                    st.session_state.content_msgs.append({
                        "role": "assistant", 
                        "content": output,
                        "image_path": image_path
                    })
                    
                except Exception as e:
                    st.error(f"Произошла ошибка: {e}")

# Обязательно для запуска через st.Page
if __name__ == "__main__":
    show()
