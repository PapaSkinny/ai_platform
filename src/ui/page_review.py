import streamlit as st
from src.agents.review_agent import get_review_agent

def show():
    st.header("⭐ Управление Репутацией")
    st.caption("Генератор умных ответов на отзывы клиентов.")

    col1, col2 = st.columns([2, 1])
    
    with col1:
        review_text = st.text_area("Текст отзыва клиента", height=150, 
                                 placeholder="Например: Товар пришел мятый, упаковка вскрыта! Ужас!")
    
    with col2:
        rating = st.feedback("stars") # Красивые звездочки Streamlit
        # st.feedback возвращает 0-4, преобразуем в 1-5. Если None, считаем 5.
        star_rating = (rating + 1) if rating is not None else 5
        
        tone = st.selectbox("Стиль ответа", 
                          ["Официально-деловой", "Дружелюбный/Заботливый", "С юмором", "Агрессивный маркетинг"])

    if st.button("Сгенерировать ответ", use_container_width=True):
        if not review_text:
            st.warning("Напишите текст отзыва!")
        else:
            with st.spinner("Пишу ответ..."):
                try:
                    chain = get_review_agent()
                    response = chain.invoke({
                        "review_text": review_text,
                        "star_rating": star_rating,
                        "tone": tone
                    })
                    
                    st.success("Готовый ответ:")
                    st.text_area("Копировать сюда:", value=response, height=250)
                    
                except Exception as e:
                    st.error(f"Ошибка: {e}")

if __name__ == "__main__":
    show() 