"""Фикстуры для тестов"""

from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from httpx import ASGITransport, AsyncClient

from src.core.db.db_manager import get_db_session
from src.settings import app_settings, db_settings
from src.main import app as fastapi_app
from tests.utils import clear_database, insert_test_data


@pytest.fixture(scope="function")
async def test_engine():
    """Тестовый движок"""
    engine = create_async_engine(db_settings.get_db_url(), echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine):
    """Сессия для тестов с откатом"""
    AsyncSessionLocal = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()  # чистим после теста


@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Клиент для запросов в тестах"""
    # Переопределяем зависимость get_db_session на тестовую сессию
    fastapi_app.dependency_overrides[get_db_session] = lambda: db_session
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="function", autouse=True)
async def default_data(db_session: AsyncSession):
    """Загрузка тестовых данных"""
    await clear_database(db_session)
    await insert_test_data(db_session)


@pytest.fixture(autouse=True)
def patch_api_key_for_tests(monkeypatch: pytest.MonkeyPatch):
    """Автоматическая фикстура для подмены API_KEY на 'test-key' во всех тестах"""
    monkeypatch.setattr(app_settings, "API_KEY", "test-key")