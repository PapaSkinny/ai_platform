from langchain.prompts import PromptTemplate
from src.utils import get_llm
from langchain_core.output_parsers import StrOutputParser

def get_review_agent():
    llm = get_llm()
    
    # Промпт принимает текст отзыва, оценку и стиль ответа
    template = """
    Ты — менеджер службы поддержки на маркетплейсе (Ozon/Wildberries).
    Твоя задача — написать ответ на отзыв клиента.
    
    Входные данные:
    - Текст отзыва: "{review_text}"
    - Оценка: {star_rating} из 5
    - Стиль ответа: {tone}
    
    Инструкции:
    1. Если оценка низкая (1-3) — прояви эмпатию, извинись, предложи решение (вернуть товар, написать в чат).
    2. Если оценка высокая (4-5) — поблагодари, пригласи за новыми покупками.
    3. Строго придерживайся заданного стиля ({tone}).
    4. Ответ должен быть на русском языке, кратким и профессиональным.
    
    Ответ:
    """
    
    prompt = PromptTemplate.from_template(template)
    
    # Используем простую цепочку (Chain), тут не нужны Tools
    chain = prompt | llm | StrOutputParser()    
    return chain