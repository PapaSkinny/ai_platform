from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from src.utils import get_llm
from src.tools.search_tools import image_finder_tool
from src.tools.design_tools import generate_image_tool
from src.tools.social_tools import telegram_poster_tool

def get_content_agent():
    llm = get_llm()
    
    tools = [image_finder_tool, generate_image_tool, telegram_poster_tool]

    prompt = ChatPromptTemplate.from_messages([
        ("system", 
         "Ты — SMM-Директор. Твоя задача — создавать контент и постить его.\n"
         "ИНСТРУМЕНТЫ:\n"
         "1. 'generate_image': Создает картинку(Промпт должен быть переведен на английский) и возвращает ИМЯ ФАЙЛА.\n"
         "2. 'post_to_telegram': Отправляет пост.\n"
         "\n"
         "ЖЕЛЕЗНОЕ ПРАВИЛО (Chain of Thought):\n"
         "Если нужно сделать пост с картинкой, делай строго по шагам:\n"
         "ШАГ 1. Вызови 'generate_image'.Описание обязательно переведи на английский. Дождись ответа инструмента.\n"
         "ШАГ 2. Прочитай имя файла из ответа (например, 'generated_image_a1b2.jpg').\n"
         "ШАГ 3. Вызови 'post_to_telegram', передав в image_path это реальное имя файла.\n"
         "\n"
         "ЗАПРЕЩЕНО:\n"
         "- Запрещено выдумывать имена файлов (напр. 'nike.jpg'), если ты их только что не сгенерировал.\n"
         "- Запрещено вызывать 'post_to_telegram' до того, как 'generate_image' вернул результат."
        ),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    
    return AgentExecutor(agent=agent, tools=tools, verbose=True)
