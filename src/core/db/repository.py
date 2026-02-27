"""Базовый репозиторий"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from src.core.db.models import Base

ModelType = TypeVar("ModelType", bound=Base)
DTOType = TypeVar("DTOType")

class BaseRepository(ABC, Generic[ModelType, DTOType]):
    """Абстрактный базовый репозиторий"""

    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    def _base_select(self) -> Select:
        """Базовый select для конкретного репозитория"""
        ...

    @abstractmethod
    def _build_dto(self, row) -> DTOType:
        """Сборка DTO из строки результата"""
        ...

    async def _execute_dto_query(self, stmt: Select) -> list[DTOType]:
        """Выполнение запроса и сборка DTO"""
        result = await self.session.execute(stmt)
        return [self._build_dto(row) for row in result.all()]