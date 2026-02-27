FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Установка postgresql-client
RUN apt-get update \
&& apt-get install -y --no-install-recommends postgresql-client \
&& rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Копируем только зависимости
COPY pyproject.toml poetry.lock ./

# Ставим все зависимости в системный Python
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Копируем код
COPY . .

# Запуск API
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]