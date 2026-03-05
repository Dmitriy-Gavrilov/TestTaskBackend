"""API роутер для организаций"""

from fastapi import APIRouter, Depends, Path, Query, status

from src.activities.repository import ActivityRepository, get_activity_repository
from src.buildings.repository import BuildingRepository, get_building_repository
from src.dependencies import check_api_key
from src.integrations.redis import RedisService, get_redis_service
from src.organizations.repository import OrganizationRepository, get_organization_repository
from src.organizations.schemas import CreateOrganizationRequest, CreateOrganizationResponse, GetOrganizationResponse, GetOrganizationsResponse, OrganizationFilters, UpdateOrganizationRequest
from src.organizations.service import OrganizationService, get_organization_service

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.get(
    "",
    summary="Получение списка организаций"
)
async def get_all_organizations(
    filters: OrganizationFilters = Query(None, description="Фильтры для поиска организаций"),
    repository: OrganizationRepository = Depends(get_organization_repository),
    service: OrganizationService = Depends(get_organization_service),
    redis_service: RedisService = Depends(get_redis_service),
    _: None = Depends(check_api_key)
) -> GetOrganizationsResponse:
    """Получить список организаций с фильтрами:
    - ID здания
    - Название организации
    - Радиус
    - Прямоугольная область
    """
    return await service.get_organizations(filters, repository, redis_service)


@router.get(
    "/{organization_id}",
    summary="Получение организации по ID"
)
async def get_organization_by_id(
    organization_id: int = Path(..., description="ID организации"),
    repository: OrganizationRepository = Depends(get_organization_repository),
    service: OrganizationService = Depends(get_organization_service),
    redis_service: RedisService = Depends(get_redis_service),
    _: None = Depends(check_api_key)
) -> GetOrganizationResponse:
    """Получить организацию по ID"""
    return await service.get_organization(organization_id, repository, redis_service)


@router.post(
    "",
    summary="Создание организации",
    status_code=status.HTTP_201_CREATED
)
async def create_organization(
    organization: CreateOrganizationRequest,
    org_repository: OrganizationRepository = Depends(get_organization_repository),
    building_repository: BuildingRepository = Depends(get_building_repository),
    activity_repository: ActivityRepository = Depends(get_activity_repository),
    service: OrganizationService = Depends(get_organization_service),
    redis_service: RedisService = Depends(get_redis_service),
    _: None = Depends(check_api_key)
) -> CreateOrganizationResponse:
    """Создать организацию
    - Проверяется наличие здания
    - Проверяется наличие видов деятельности
    - Добавляются переданные телефоны
    """
    return await service.create_organization(
        organization,
        org_repository,
        building_repository,
        activity_repository,
        redis_service
    )


@router.patch(
    "/{organization_id}",
    summary="Обновление организации"
)
async def update_organization(
    organization: UpdateOrganizationRequest,
    organization_id: int = Path(..., description="ID организации"),
    org_repository: OrganizationRepository = Depends(get_organization_repository),
    building_repository: BuildingRepository = Depends(get_building_repository),
    activity_repository: ActivityRepository = Depends(get_activity_repository),
    service: OrganizationService = Depends(get_organization_service),
    redis_service: RedisService = Depends(get_redis_service),
    _: None = Depends(check_api_key)
) -> None:
    """
    Обновить организацию
    Заменяются все переданные поля
    """
    return await service.update_organization(
        organization_id,
        organization,
        org_repository,
        building_repository,
        activity_repository,
        redis_service
    )


@router.delete(
    "/{organization_id}",
    summary="Удаление организации",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_organization(
    organization_id: int = Path(..., description="ID организации"),
    org_repository: OrganizationRepository = Depends(get_organization_repository),
    service: OrganizationService = Depends(get_organization_service),
    redis_service: RedisService = Depends(get_redis_service),
    _: None = Depends(check_api_key)
) -> None:
    """Удалить организацию"""
    await service.delete_organization(organization_id, org_repository, redis_service)
