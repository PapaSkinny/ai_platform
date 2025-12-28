from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from src.utils import get_llm

# Глобальная переменная для хранения текущей базы данных
# (Streamlit перезапускает скрипт, но модули кэшируются, так что это сработает)
CURRENT_VECTOR_STORE = None

def set_vector_store(vector_store):
    """Функция, чтобы передать базу данных внутрь модуля"""
    global CURRENT_VECTOR_STORE
    CURRENT_VECTOR_STORE = vector_store

@tool("search_knowledge_base")
def search_knowledge_base(query: str):
    """
    Ищет информацию в загруженном документе.
    Вход: конкретный вопрос или ключевые слова.
    Выход: цитаты из документа.
    """
    global CURRENT_VECTOR_STORE
    if not CURRENT_VECTOR_STORE:
        return "Ошибка: База знаний не загружена. Попросите пользователя загрузить файл."
    
    # Ищем 4 самых похожих куска текста
    results = CURRENT_VECTOR_STORE.similarity_search(query, k=4)
    
    # Собираем их в один текст
    context = "\n\n".join([doc.page_content for doc in results])
    return context

def get_rag_agent():
    llm = get_llm()
    
    tools = [search_knowledge_base]

    prompt = ChatPromptTemplate.from_messages([
        ("system", 
         "Ты — Эксперт по Документации (RAG). Твоя задача — отвечать на вопросы СТРОГО по документу.\n"
         "ИНСТРУКЦИИ:\n"
         "1. Для любого вопроса по содержанию используй инструмент `search_knowledge_base`.\n"
         "2. Прочитай найденный контекст.\n"
         "3. Сформулируй ответ, опираясь ТОЛЬКО на этот контекст.\n"
         "4. Если в контексте нет ответа, так и скажи: 'В документе нет информации об этом'. НЕ выдумывай."
        ),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    
    return AgentExecutor(agent=agent, tools=tools, verbose=True)