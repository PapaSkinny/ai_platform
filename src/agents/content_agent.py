from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from src.utils import get_llm
from src.tools.search_tools import image_finder_tool
from src.tools.design_tools import generate_image_tool
from src.tools.social_tools import telegram_poster_tool


def get_content_agent():
    """
    Агент для создания SMM-контента.
    """
    llm = get_llm()

    tools = [image_finder_tool, generate_image_tool, telegram_poster_tool]

    # TODO: настроить промпту и связать с инструментами
    prompt = ChatPromptTemplate.from_messages([])

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)
