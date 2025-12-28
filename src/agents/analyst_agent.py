import pandas as pd
import matplotlib.pyplot as plt
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_core.tools import tool
from src.utils import get_llm

class AnalystManager:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.llm = get_llm()

    def get_tool(self):
        # Инструкция с принудительным переключением бэкенда графиков
        prefix = """
        Ты — аналитик данных. Твоя задача — выполнять вычисления на Python.
        
        ВАЖНЫЕ ПРАВИЛА:
        1. Сначала проанализируй текст запроса пользовател и пойми какой товар пользователь хочет проанализировать.
            Если хочет юзер просто хочет получить данные о товаре, то в запросе он напишет название продукта.
            Например:"Запрос пользователя:" "Цена на PS5" или "Прибыль по товару Айфон 15".
            Тогда используй df['Product'] == 'PS5' или df['Product'] == 'Айфон 15' соответственно.
            Если пользователь просит построить график:
           - В начале кода ВСЕГДА пиши: import matplotlib.pyplot as plt; plt.switch_backend('Agg')
           - Создай график.
           ВАЖНО: график должен быть сохранен обязательно как 'plot.png', другие названия для файла запрещены
           - Сохрани файл командой: plt.savefig('plot.png')
           - НЕ используй plt.show().
           - В финальном ответе напиши ТОЛЬКО: "График сохранен как plot.png".
        
        2. Для расчетов просто верни результат текстом.
        """
        
        inner_agent = create_pandas_dataframe_agent(
            self.llm,
            self.df,
            verbose=True,
            allow_dangerous_code=True,
            agent_type="openai-tools",
            prefix=prefix,
            handle_parsing_errors=True
        )

        @tool("analyze_file_data")
        def analyze_tool(query: str):
            """
            Анализирует таблицу. Строит графики через Matplotlib.
            Вход: вопрос пользователя (например: 'Построй график продаж').
            """
            try:
                # Очищаем старые фигуры в памяти перед запуском, чтобы графики не накладывались
                plt.clf()
                plt.close('all')
                
                result = inner_agent.invoke(query)
                return result["output"]
            except Exception as e:
                return f"Ошибка при выполнении кода: {e}"

        return analyze_tool
