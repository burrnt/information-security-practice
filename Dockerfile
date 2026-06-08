# ЕТАП 1: Збірка залежностей (Builder)
FROM python:3.11-slim AS builder

WORKDIR /app

# Створюємо чисте віртуальне середовище в папці /opt/venv
RUN python -m venv /opt/venv
# Активуємо його для цього етапу (додаємо в PATH)
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ЕТАП 2: Фінальний захищений образ
FROM python:3.11-slim

# Створюємо non-root користувача appuser
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# КРИТИЧНИЙ КРОК: Копіюємо все venv і ОДРАЗУ робимо власником нашого appuser (--chown)
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv
# Прописуємо шлях до бінарників venv у PATH системи
ENV PATH="/opt/venv/bin:$PATH"

# Копіюємо код додатку та теж робимо власником appuser
COPY --chown=appuser:appuser ./app ./app

# Створюємо папку для бази даних та даємо на неї повні права користувачу appuser
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Перемикаємо контейнер на роботу від імені безпечного користувача
USER appuser

# HEALTHCHECK
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')" || exit 1

EXPOSE 8000

# Запуск Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
