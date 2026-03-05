"""Репозиторий для работы со зданиями"""

from fastapi import Depends
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_X, ST_Y
from sqlalchemy import Select, cast, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db_manager import get_db_session
from src.core.db.repository import BaseRepository
from src.core.db.models import Building
from src.core.dto.building import BuildingDTO


class BuildingRepository(BaseRepository[Building, BuildingDTO]):
    """Репозиторий для работы со зданиями"""

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    def _base_select(self) -> Select:
        """Базовый select для зданий"""
        return select(
            Building.id,
            Building.address,
            ST_X(cast(Building.location, Geometry)).label("longitude"),
            ST_Y(cast(Building.location, Geometry)).label("latitude"),
        )
    
    def _build_dto(self, row) -> BuildingDTO:
        """Сборка DTO из строки результата"""
        return BuildingDTO(
            id=row.id,
            address=row.address,
            latitude=row.latitude,
            longitude=row.longitude,
        )
    
    async def get_by_id(self, building_id: int) -> BuildingDTO | None:
        """Получить здание по ID"""
        stmt = self._base_select().where(Building.id == building_id)
        result = (await self.session.execute(stmt)).first()
        if result is None:
            return None
        return self._build_dto(result)


def get_building_repository(session: AsyncSession = Depends(get_db_session)) -> BuildingRepository:
    """Фабрика для создания репозитория зданий"""
    return BuildingRepository(session)