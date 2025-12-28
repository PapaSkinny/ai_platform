import streamlit as st
from src.ui import styles # Импортируем наш CSS

# 1. Настройка страницы (должна быть первой командой)
st.set_page_config(
    page_title="AI Nexus Platform", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Применяем CSS стили
styles.apply_custom_css()

# 3. Сайдбар: Лого и статус
with st.sidebar:
    # Можно использовать st.image("logo.png") если есть
    st.markdown("# ⚡ AI Nexus") 
    st.caption("v1.2.0 • Enterprise Edition")
    
    st.markdown("---")
    
    # Метрики системы (для вида "Dashboard")
    col1, col2 = st.columns(2)
    col1.metric("LLM", "GigaChat", delta="Active")
    col2.metric("Search", "Tavily", delta="Online")
    
    st.markdown("---")
    
    st.info("💡 **Совет:** Используйте 'Контент Мейкер' для авто-постинга в Telegram.")

# 4. Навигация
st.sidebar.title("Модули")

pg = st.navigation([
    st.Page(page_analyst.py, title="Бизнес-Аналитик", icon="📊"),
    st.Page(page_content.py, title="SMM & Дизайн", icon="🎨"),
    st.Page(page_review.py, title="Репутация (Отзывы)", icon="⭐"),
    st.Page(page_rag.py, title="База Знаний (Docs)", icon="📚")
])

pg.run()
