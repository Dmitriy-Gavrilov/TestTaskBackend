"""Репозиторий для работы с организациями"""

from geoalchemy2 import Geometry
from sqlalchemy import ColumnElement, Row, Select, cast, exists, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_X, ST_Y, ST_DWithin, ST_MakeEnvelope, ST_MakePoint
from sqlalchemy.sql.functions import array_agg
from fastapi import Depends

from src.core.db.repository import BaseRepository
from src.core.db.models import (
    SRID_WGS84,
    Activity,
    Organization,
    OrganizationPhone,
    organization_activities,
    Building,
)
from src.core.db.db_manager import get_db_session
from src.core.dto.activity import ActivityDTO
from src.core.dto.building import BuildingDTO
from src.core.dto.organization import OrganizationDTO


class OrganizationRepository(BaseRepository[Organization, OrganizationDTO]):
    """Репозиторий для работы с организациями"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    def _base_select(self) -> Select:
        """Базовый запрос с агрегацией связанных данных"""
        stmt = (
            select(
                Organization.id,
                Organization.name,
                Building.id.label("building_id"),
                Building.address,
                ST_X(cast(Building.location, Geometry)).label("longitude"),
                ST_Y(cast(Building.location, Geometry)).label("latitude"),
                func.coalesce(array_agg(func.distinct(OrganizationPhone.phone)), []).label("phones"),
                func.coalesce(array_agg(func.distinct(Activity.id)), []).label("activity_ids"),
                func.coalesce(array_agg(func.distinct(Activity.name)), []).label("activity_names"),
            )
            .join(Building, Organization.building_id == Building.id)
            .outerjoin(OrganizationPhone, OrganizationPhone.organization_id == Organization.id)
            .outerjoin(organization_activities, organization_activities.c.organization_id == Organization.id)
            .outerjoin(Activity, Activity.id == organization_activities.c.activity_id)
            .group_by(Organization.id, Building.id)
        )
        return stmt

    def _build_dto(self, row: Row) -> OrganizationDTO:
        """Сброка OrganizationDTO из данных запроса"""
        activities = [
            ActivityDTO(id=aid, name=aname)
            for aid, aname in zip(row.activity_ids, row.activity_names)
            if aid
        ]
        building = BuildingDTO(
            id=row.building_id, address=row.address, longitude=row.longitude, latitude=row.latitude
        )
        dto = OrganizationDTO(
            id=row.id, name=row.name, phones=row.phones, activities=activities, building=building
        )
        return dto
    
    async def _execute_dto_query(self, stmt: Select) -> list[OrganizationDTO]:
        """Выполнение запроса и преобразование результатов в DTO"""
        result = await self.session.execute(stmt)
        dtos = []
        for row in result.all():
            dtos.append(self._build_dto(row))
        return dtos

    def _stmt_by_building_id(self, building_id: int) -> ColumnElement[bool]:
        """Получение организаций по id здания"""
        return Organization.building_id == building_id
    
    def _stmt_by_activity_name(self, activity_name: str) -> ColumnElement[bool]:
        """Получение организаций по названию деятельности (включая дочерние активности)"""
        # рекурсивный CTE для поиска активности и дочерних
        activity_cte = (
            select(Activity.id)
            .where(Activity.name == activity_name)
            .cte(name="activity_tree", recursive=True)
        )
        activity_cte = activity_cte.union_all(
            select(Activity.id).where(Activity.parent_id == activity_cte.c.id)
        )

        subq = (
            select(organization_activities.c.organization_id)
            .where(
                (organization_activities.c.organization_id == Organization.id) &
                (organization_activities.c.activity_id.in_(select(activity_cte.c.id)))
            )
            .correlate(Organization)
        )

        return exists(subq)
    
    def _stmt_by_name(self, name: str) -> ColumnElement[bool]:
        """Получение организаций по названию"""
        return Organization.name == name
    
    def _stmt_by_radius(
        self,
        latitude: float,
        longitude: float,
        radius_meters: float,
    ) -> ColumnElement[bool]:
        """Получение организаций по радиусу"""
        point = ST_MakePoint(longitude, latitude)
        return ST_DWithin(Building.location, point, radius_meters)
    
    def _stmt_by_bbox(
        self,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
    ) -> ColumnElement[bool]:
        """Получение организаций по bounding box"""
        envelope = ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, SRID_WGS84)
        return Building.location.ST_Intersects(envelope)

    async def get_with_filters(
        self,
        *,
        building_id: int | None = None,
        activity_name: str | None = None,
        name: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        radius: float | None = None,
        min_lat: float | None = None,
        max_lat: float | None = None,
        min_lon: float | None = None,
        max_lon: float | None = None,
    ) -> list[OrganizationDTO]:
        """Получение организаций с фильтрацией"""
        stmt = self._base_select()
        if building_id:
            stmt = stmt.where(self._stmt_by_building_id(building_id))
        if activity_name:
            stmt = stmt.where(self._stmt_by_activity_name(activity_name))
        if name:
            stmt = stmt.where(self._stmt_by_name(name))
        if latitude and longitude and radius:
            stmt = stmt.where(self._stmt_by_radius(latitude, longitude, radius))
        if min_lat and max_lat and min_lon and max_lon:
            stmt = stmt.where(self._stmt_by_bbox(min_lat, min_lon, max_lat, max_lon))

        return await self._execute_dto_query(stmt)
    
    async def get_by_id(self, organization_id: int) -> OrganizationDTO | None:
        """Получение организации по ID"""
        result = (
            await self.session.execute(
                self._base_select()
                .where(Organization.id == organization_id)
            )
        ).first()
        if result is None:
            return None
        return self._build_dto(result)


def get_organization_repository(session: AsyncSession = Depends(get_db_session)) -> OrganizationRepository:
    """Фабрика для создания репозитория организаций"""
    return OrganizationRepository(session)
