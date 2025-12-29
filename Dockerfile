FROM python:3.11-slim-bookworm

# Отключаем буферизацию (чтобы видеть логи)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Устанавливаем ТОЛЬКО то, что реально нужно
# Убрали software-properties-common, из-за которого была ошибка
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Копируем зависимости
COPY requirements.txt .

# 2. Обновляем pip
RUN pip install --no-cache-dir --upgrade pip
# 3. ВАЖНО: Сначала ставим PyTorch CPU (легкий)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 4. Ставим остальные библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Порт
EXPOSE 8501

# Проверка здоровья
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Запуск
ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]