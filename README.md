# Тестовое задание Backend Python

## Описание проекта

Organizations API — это веб-сервис на базе FastAPI для управления информацией об организациях, зданиях и их видах деятельности. Проект поддерживает географические запросы с использованием PostGIS для работы с пространственными данными.

### Основные возможности:
- Получение списка организаций с расширенной фильтрацией
- Поиск организаций по ID
- Географический поиск по радиусу и прямоугольной области
- Фильтрация по зданиям, видам деятельности и названиям
- Поддержка иерархической структуры видов деятельности

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
└── organizations/              # Модуль организаций
    ├── router.py              # API роутеры
    ├── schemas.py             # Pydantic схемы
    ├── service.py             # Бизнес-логика
    └── repository.py          # Репозиторий организаций
```

## Локальный запуск

### Требования
- Python 3.13+
- Docker и Docker Compose
- Poetry (для управления зависимостями)

### Запуск через Docker Compose
*Предполагается bash-окружение*

1. **Клонирование репозитория и настройка окружения:**
   ```bash
   git clone <repository-url>
   cd TestTaskBackend
   cp .env.example .env
   ```

2. **Запуск сервисов:**
   ```bash
   docker compose up --build
   ```
   
   Эта команда запустит:
   - PostgreSQL с PostGIS для географических данных
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

## Технологический стек

- **FastAPI** — веб-фреймворк
- **Pydantic** — валидация данных
- **PostgreSQL + PostGIS** — база данных с поддержкой географических данных
- **SQLAlchemy** — ORM для работы с базой данных
- **AsyncPG** — асинхронный драйвер PostgreSQL
- **Alembic** — миграции базы данных
- **Pytest**, **httpx** — тестирование
- **Docker** — контейнеризация
- **Poetry** — менеджер зависимостей
