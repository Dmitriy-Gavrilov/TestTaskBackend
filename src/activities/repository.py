"""Репозиторий для работы с видами деятельности"""

from fastapi import Depends
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db_manager import get_db_session
from src.core.db.repository import BaseRepository
from src.core.db.models import Activity
from src.core.dto.activity import ActivityDTO


class ActivityRepository(BaseRepository[Activity, ActivityDTO]):
    """Репозиторий для работы с видами деятельности"""

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    def _base_select(self) -> Select:
        """Базовый select для видов деятельности"""
        return select(Activity)
    
    def _build_dto(self, row) -> ActivityDTO:
        """Сборка DTO из строки результата"""
        return ActivityDTO(
            id=row.id,
            name=row.name,
        )

    async def get_existing_ids(self, ids: list[int]) -> set[int]:
        """
        Возвращает множество существующих id активностей из переданного списка"""
        if not ids:
            return set()

        stmt = select(Activity.id).where(Activity.id.in_(ids))
        result = await self.session.scalars(stmt)
        return set(result.all())

    async def check_all_exist(self, ids: list[int]) -> bool:
        """
        Проверяет, существуют ли все переданные активности"""
        existing_ids = await self.get_existing_ids(ids)
        return len(existing_ids) == len(set(ids))


def get_activity_repository(session: AsyncSession = Depends(get_db_session)) -> ActivityRepository:
    """Фабрика для создания репозитория видов деятельности"""
    return ActivityRepository(session)