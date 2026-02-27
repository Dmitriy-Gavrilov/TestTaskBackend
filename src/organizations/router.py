"""API роутер для организаций"""

from fastapi import APIRouter, Depends, Path, Query

from src.dependencies import check_api_key
from src.organizations.repository import OrganizationRepository, get_organization_repository
from src.organizations.schemas import GetOrganizationResponse, GetOrganizationsResponse, OrganizationFilters
from src.organizations.service import OrganizationService, get_organization_service

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.get(
    "",
    description="Получение списка организаций"
)
async def get_all_organizations(
    filters: OrganizationFilters = Query(None, description="Фильтры для поиска организаций"),
    repository: OrganizationRepository = Depends(get_organization_repository),
    service: OrganizationService = Depends(get_organization_service),
    _: None = Depends(check_api_key)
) -> GetOrganizationsResponse:
    """Получить список организаций с фильтрами:
    - ID здания
    - Название организации
    - Радиус
    - Прямоугольная область
    """
    return await service.get_organizations(filters, repository)


@router.get(
    "/{organization_id}",
    description="Получение организации по ID"
)
async def get_organization_by_id(
    organization_id: int = Path(..., description="ID организации"),
    repository: OrganizationRepository = Depends(get_organization_repository),
    service: OrganizationService = Depends(get_organization_service),
    _: None = Depends(check_api_key)
) -> GetOrganizationResponse:
    """Получить организацию по ID"""
    return await service.get_organization(organization_id, repository)