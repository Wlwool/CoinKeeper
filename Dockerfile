# Dockerfile
FROM python:3.13-slim

# базовые зависимости для сборки некоторых пакетов и для проверки Redis
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    redis-tools \
 && rm -rf /var/lib/apt/lists/*

# создание непривилегированного пользователя
ARG APP_USER=appuser
RUN useradd --create-home --shell /bin/bash ${APP_USER}

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# права
RUN chown -R ${APP_USER}:${APP_USER} /app
USER ${APP_USER}

# entrypointдождётся Redis и запустит main.py
COPY --chown=${APP_USER}:${APP_USER} entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV PYTHONUNBUFFERED=1
WORKDIR /app

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "main.py"]
