#!/usr/bin/env bash
set -e

# простая функция ожидания Redis
wait_for_redis() {
  host="${REDIS_HOST:-redis}"
  port="${REDIS_PORT:-6379}"
  if [ -n "${REDIS_PASSWORD}" ]; then
    auth_args="-a ${REDIS_PASSWORD}"
  else
    auth_args=""
  fi

  echo "Ожидаем Redis на ${host}:${port}..."
  # пробуем redis-cli ping
  until redis-cli -h "$host" -p "$port" $auth_args ping >/dev/null 2>&1; do
    echo "Redis недоступен, ждём 1s..."
    sleep 1
  done
  echo "Redis доступен."
}

# если нужно ждём Redis
if [ "${USE_REDIS:-false}" = "true" ] || [ "${USE_REDIS:-false}" = "1" ]; then
  wait_for_redis
fi

# запускаем приложение
exec "$@"


