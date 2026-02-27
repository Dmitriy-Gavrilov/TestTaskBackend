#!/bin/bash
# run_tests.sh

# Название контейнера
CONTAINER_NAME="api"

# Команда для запуска pytest внутри контейнера
docker compose exec -it "$CONTAINER_NAME" pytest tests "$@"