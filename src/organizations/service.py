"""Сервис для работы с организациями"""

from fastapi import HTTPException, status

from src.core.dto.organization import OrganizationDTO
from src.organizations.repository import OrganizationRepository
from src.organizations.schemas import BuildingSchema, GetOrganizationResponse, GetOrganizationsResponse, OrganizationFilters, OrganizationSchema


class OrganizationService:
    """Сервис для работы с организациями"""
    
    def _build_organization_response(
        self,
        organization: OrganizationDTO
    ) -> OrganizationSchema:
        """Построение ответа для организации"""
        return OrganizationSchema(
            id=organization.id,
            name=organization.name,
            phones=organization.phones,
            building=BuildingSchema(**organization.building.to_dict()),
            activities=[a.name for a in organization.activities],
        )
    
    async def get_organizations(
        self,
        filters: OrganizationFilters,
        repo: OrganizationRepository
    ) -> GetOrganizationsResponse:
        """Получить организации с фильтрацией"""
        result = await repo.get_with_filters(
            building_id=filters.building_id,
            activity_name=filters.activity_name,
            name=filters.name,
            latitude=filters.radius_lat,
            longitude=filters.radius_lng,
            radius=filters.radius_meters,
            min_lat=filters.min_lat,
            max_lat=filters.max_lat,
            min_lon=filters.min_lon,
            max_lon=filters.max_lon,
        )

        organizations = [self._build_organization_response(org) for org in result]

        return GetOrganizationsResponse(organizations=organizations)

    async def get_organization(
        self,
        organization_id: int,
        repo: OrganizationRepository
    ) -> GetOrganizationResponse:
        """Получить организацию по ID"""
        result = await repo.get_by_id(organization_id)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Организация не найдена"
            )
        return GetOrganizationResponse(organization=self._build_organization_response(result))


def get_organization_service() -> OrganizationService:
    """Фабрика для создания сервиса организаций"""
    return OrganizationService()
