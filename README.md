# Тестовое задание Backend Python

## Описание проекта

Organizations API — это веб-сервис на базе FastAPI для управления информацией об организациях, зданиях и их видах деятельности. Проект поддерживает географические запросы с использованием PostGIS для работы с пространственными данными.

### Основные возможности:
- Получение списка организаций с расширенной фильтрацией
- Поиск организаций по ID
- Географический поиск по радиусу и прямоугольной области
- Фильтрация по зданиям, видам деятельности и названиям
- Поддержка иерархической структуры видов деятельности
- Создание новых организаций
- Обновление существующих организаций
- Удаление организаций

## Структура проекта

```
src/
├── main.py                    # Точка входа в приложение
├── settings.py                # Настройки приложения и базы данных
├── dependencies.py            # Зависимости FastAPI
├── core/                      # Ядро приложения
│   ├── db/                    # Работа с базой данных
│   │   ├── models.py          # SQLAlchemy модели
│   │   ├── db_manager.py      # Менеджер подключения к БД
│   │   └── repository.py      # Базовый репозиторий
│   └── dto/                   # Объекты передачи данных
│       ├── organization.py    # DTO для организаций
│       ├── building.py        # DTO для зданий
│       └── activity.py        # DTO для видов деятельности
├── activities/                # Модуль видов деятельности
│   └── repository.py          # Репозиторий видов деятельности
├── buildings/                 # Модуль зданий
│   └── repository.py          # Репозиторий зданий
├── integrations/              # Интеграции с внешними сервисами
│   └── redis.py               # Сервис Redis для кэширования
└── organizations/              # Модуль организаций
    ├── router.py              # API роутеры
    ├── schemas.py             # Pydantic схемы
    ├── service.py             # Бизнес-логика
    └── repository.py          # Репозиторий организаций
```

## Кэширование

Проект использует Redis для кэширования данных с целью повышения производительности API.

### Как работает кэширование

- **Кэшируемые данные**: Ответы на запросы получения списка организаций (`GET /api/organizations`) и получения организации по ID (`GET /api/organizations/{id}`).
- **Ключи кэша**:
  - Для списка организаций: `cache:organizations:{filters}` (где `{filters}` — сериализованный словарь параметров фильтрации)
  - Для конкретной организации: `cache:organization:{id}`
- **Время жизни кэша**: 5 минут (300 секунд)
- **Формат хранения**: Данные сериализуются в JSON с помощью Pydantic моделей

### Инвалидация кэша

При изменении данных кэш автоматически очищается:
- **Создание организации** (`POST /api/organizations`): Удаляется кэш по паттерну `cache:organizations:*`
- **Обновление организации** (`PATCH /api/organizations/{id}`): Удаляется кэш конкретной организации `cache:organization:{id}` и по паттерну `cache:organizations:*`
- **Удаление организации** (`DELETE /api/organizations/{id}`): Удаляется кэш конкретной организации `cache:organization:{id}` и по паттерну `cache:organizations:*`

### Удаление кэша по паттерну

Redis-сервис поддерживает удаление кэша по паттерну с использованием команды `KEYS`. Это позволяет эффективно очищать группы связанных кэшей без необходимости перечисления всех ключей вручную.

## Локальный запуск

### Требования
- Python 3.13+
- Docker и Docker Compose
- Poetry (для управления зависимостями)

### Запуск через Docker Compose
*Предполагается bash-окружение*

1. **Клонирование репозитория и настройка окружения:**
   ```bash
   git clone https://github.com/Dmitriy-Gavrilov/TestTaskBackend.git
   cd TestTaskBackend
   cp .env.example .env
   ```

2. **Запуск сервисов:**
   ```bash
   docker compose up --build
   ```
   
   Эта команда запустит:
   - PostgreSQL с PostGIS для географических данных
   - Redis для кэширования данных
   - Автоматическую миграцию базы данных через Alembic
   - FastAPI приложение на порту 8000

3. **Проверка работы:**
   - API будет доступен по адресу: http://localhost:8000
   - Документация API: http://localhost:8000/docs
   - Альтернативная документация: http://localhost:8000/redoc

### Запуск тестов

Для запуска тестов используется Docker:

```bash
# Запуск всех тестов
./run_tests.sh

# Запуск конкретного теста
./run_tests.sh tests/organizations/test_organizations_e2e.py::TestOrganizationsAPI::test_get_orgs_with_filter_bbox
```

**Тестовое покрытие проекта составляет >90%**.

### Примеры запросов

**Получение всех организаций:**
```bash
curl -H "X-API-Key: test-secret-key" "http://localhost:8000/api/organizations"
```

**Поиск по названию:**
```bash
curl -H "X-API-Key: test-secret-key" "http://localhost:8000/api/organizations?name=Кафе"
```

**Географический поиск по радиусу:**
```bash
curl -H "X-API-Key: test-secret-key" \
  "http://localhost:8000/api/organizations?radius_lat=55.7558&radius_lng=37.6173&radius_meters=1000"
```

**Поиск в прямоугольной области:**
```bash
curl -H "X-API-Key: test-secret-key" \
  "http://localhost:8000/api/organizations?min_lat=55.7&min_lon=37.6&max_lat=55.8&max_lon=37.7"
```

**Создание новой организации:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-secret-key" \
  -d '{"name": "Новая организация", "phones": ["+71234567890"], "building_id": 1, "activity_ids": [1,2]}' \
  http://localhost:8000/api/organizations
```

**Обновление организации:**
```bash
curl -X PATCH \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-secret-key" \
  -d '{"name": "Обновленное название"}' \
  http://localhost:8000/api/organizations/1
```

**Удаление организации:**
```bash
curl -X DELETE \
  -H "X-API-Key: test-secret-key" \
  http://localhost:8000/api/organizations/1
```

## Технологический стек

- **FastAPI** — веб-фреймворк
- **Pydantic** — валидация данных
- **PostgreSQL + PostGIS** — база данных с поддержкой географических данных
- **Redis** — кэширование данных
- **SQLAlchemy** — ORM для работы с базой данных
- **AsyncPG** — асинхронный драйвер PostgreSQL
- **Alembic** — миграции базы данных
- **Pytest**, **httpx** — тестирование
- **Docker** — контейнеризация
- **Poetry** — менеджер зависимостей
