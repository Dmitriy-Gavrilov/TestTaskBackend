"""Сервис для работы с организациями"""

from fastapi import HTTPException, status

from src.activities.repository import ActivityRepository
from src.buildings.repository import BuildingRepository
from src.core.dto.building import BuildingDTO
from src.core.dto.organization import (
    CreateOrganizationDTO,
    OrganizationDTO,
    UpdateOrganizationDTO,
)
from src.integrations.redis import RedisService
from src.organizations.repository import OrganizationRepository
from src.organizations.schemas import (
    BuildingSchema,
    CreateOrganizationRequest,
    CreateOrganizationResponse,
    GetOrganizationResponse,
    GetOrganizationsResponse,
    OrganizationFilters,
    OrganizationSchema,
    UpdateOrganizationRequest,
)


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
    
    async def _check_organization_exists(
        self,
        organization_id: int,
        repo: OrganizationRepository
    ) -> OrganizationDTO:
        """Проверка существования организации"""
        organization = await repo.get_by_id(organization_id)
        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Организация не найдена"
            )
        return organization
    
    async def _check_building_exists(
        self,
        building_id: int,
        repo: BuildingRepository
    ) -> BuildingDTO:
        """Проверка существования здания"""
        building = await repo.get_by_id(building_id)
        if building is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Здание не найдено"
            )
        return building
    
    async def _check_activities_exists(
        self,
        activity_ids: list[int],
        repo: ActivityRepository
    ) -> None:
        """Проверка существования активностей"""
        if not await repo.check_all_exist(activity_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Одна или несколько видов деятельности не найдены"
            )
    
    async def get_organizations(
        self,
        filters: OrganizationFilters,
        repo: OrganizationRepository,
        redis_service: RedisService
    ) -> GetOrganizationsResponse:
        """Получить организации с фильтрацией"""
        cache_key = f"organizations:{filters.model_dump()}"
        cached = await redis_service.get_cache(cache_key, GetOrganizationsResponse)
        if cached:
            return GetOrganizationsResponse.model_validate(cached)

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

        response = GetOrganizationsResponse(organizations=organizations)
        await redis_service.set_cache(cache_key, response, ex=300)

        return response

    async def get_organization(
        self,
        organization_id: int,
        repo: OrganizationRepository,
        redis_service: RedisService
    ) -> GetOrganizationResponse:
        """Получить организацию по ID"""
        cache_key = f"organization:{organization_id}"
        cached = await redis_service.get_cache(cache_key, GetOrganizationResponse)
        if cached:
            return GetOrganizationResponse.model_validate(cached)

        org = await self._check_organization_exists(organization_id, repo)
        response = GetOrganizationResponse(organization=self._build_organization_response(org))

        await redis_service.set_cache(cache_key, response, ex=300)
        return response

    async def create_organization(
        self,
        organization: CreateOrganizationRequest,
        org_repo: OrganizationRepository,
        building_repo: BuildingRepository,
        activity_repo: ActivityRepository,
        redis_service: RedisService
    ) -> CreateOrganizationResponse:
        """Создать организацию"""
        await self._check_building_exists(organization.building_id, building_repo)
        
        await self._check_activities_exists(organization.activity_ids, activity_repo)

        res = await org_repo.create(CreateOrganizationDTO(
            name=organization.name,
            phones=organization.phones,
            building_id=organization.building_id,
            activity_ids=organization.activity_ids
        ))

        await redis_service.del_cache_pattern("organizations:*")

        return CreateOrganizationResponse(id=res)


    async def update_organization(
        self,
        organization_id: int,
        organization: UpdateOrganizationRequest,
        org_repo: OrganizationRepository,
        building_repo: BuildingRepository,
        activity_repo: ActivityRepository,
        redis_service: RedisService
    ) -> None:
        """Обновить организацию"""
        await self._check_organization_exists(organization_id, org_repo)

        if organization.building_id is not None:
            await self._check_building_exists(organization.building_id, building_repo)
        
        if organization.activity_ids is not None:
            await self._check_activities_exists(organization.activity_ids, activity_repo)

        await org_repo.update(organization_id, UpdateOrganizationDTO(
            name=organization.name,
            phones=organization.phones,
            building_id=organization.building_id,
            activity_ids=organization.activity_ids
        ))

        await redis_service.del_cache(f"organization:{organization_id}")
        await redis_service.del_cache_pattern("organizations:*")

    async def delete_organization(
        self,
        organization_id: int,
        org_repo: OrganizationRepository,
        redis_service: RedisService
    ) -> None:
        """Удалить организацию"""
        await self._check_organization_exists(organization_id, org_repo)
        await org_repo.delete(organization_id)

        await redis_service.del_cache(f"organization:{organization_id}")
        await redis_service.del_cache_pattern("organizations:*")


def get_organization_service() -> OrganizationService:
    """Фабрика для создания сервиса организаций"""
    return OrganizationService()
