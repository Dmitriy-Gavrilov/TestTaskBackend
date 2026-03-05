"""Тесты кэширования организаций"""

from unittest.mock import AsyncMock

from src.core.dto.activity import ActivityDTO
from src.core.dto.building import BuildingDTO
from src.core.dto.organization import OrganizationDTO
from src.organizations.schemas import GetOrganizationResponse, UpdateOrganizationRequest
from src.organizations.service import OrganizationService
from src.organizations.repository import OrganizationRepository

class TestOrganizationCache:
    """Тесты кэширования организаций"""

    def _mock_repo(self) -> AsyncMock:
        """Мок репозитория организаций"""
        repo_mock = AsyncMock(spec=OrganizationRepository)

        async def get_by_id_side_effect(org_id: int) -> OrganizationDTO:
            return OrganizationDTO(
                id=org_id,
                name="Test Org",
                phones=["+77777777777"],
                building=BuildingDTO(id=1, address="Test Address", longitude=0.0, latitude=0.0),
                activities=[ActivityDTO(id=1, name="Activity1")],
            )

        repo_mock.get_by_id.side_effect = get_by_id_side_effect
        return repo_mock

    async def test_organization_get_cached(self, redis_service_test) -> None:
        """Организация кэшируется в Redis"""
        org_id = 1
        repo_mock = self._mock_repo()
        service = OrganizationService()

        # Первый вызов — должен попасть в репозиторий
        response1 = await service.get_organization(org_id, repo_mock, redis_service_test)
        assert response1.organization.name == "Test Org"
        assert repo_mock.get_by_id.called

        repo_mock.get_by_id.reset_mock()

        # Второй вызов — данные должны быть из Redis
        response2 = await service.get_organization(org_id, repo_mock, redis_service_test)
        assert response2.organization.name == "Test Org"
        repo_mock.get_by_id.assert_not_called()

    async def test_organization_cache_invalidation_on_update(self, redis_service_test) -> None:
        """Кэш сбрасывается при обновлении"""
        org_id = 1
        repo_mock = self._mock_repo()
        service = OrganizationService()

        await service.get_organization(org_id, repo_mock, redis_service_test)

        # Проверка кэша
        cache_key = f"organization:{org_id}"
        cached_before = await redis_service_test.get_cache(cache_key, GetOrganizationResponse)
        assert cached_before is not None

        # Инвалидация кэша
        await service.update_organization(
            org_id,
            UpdateOrganizationRequest(name="Updated Org"),
            repo_mock,
            building_repo=AsyncMock(),
            activity_repo=AsyncMock(),
            redis_service=redis_service_test,
        )

        # Проверка, что кэщ очищен
        cached_after = await redis_service_test.get_cache(cache_key, GetOrganizationResponse)
        assert cached_after is None

        # Следующий вызов get_organization снова должен попасть в репозиторий
        repo_mock.get_by_id.reset_mock()
        await service.get_organization(org_id, repo_mock, redis_service_test)
        repo_mock.get_by_id.assert_called_once()
