FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВСЮ папку FastAPI в /app
COPY . .

# Устанавливаем PYTHONPATH
ENV PYTHONPATH=/app

# Запускаем main.py (он в папке project_fastapi)
CMD ["uvicorn", "project_fastapi.main:app", "--host", "0.0.0.0", "--port", "8000"]