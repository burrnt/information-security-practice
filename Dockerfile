FROM python:3.11-slim

WORKDIR /app_code

# Копіюємо залежності окремим шаром (кешування)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код
COPY . .

# Створюємо директорію для бази даних
RUN mkdir -p /app_code/data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
