"""Тесты для API организаций"""

from httpx import AsyncClient, Response
from fastapi import status

class TestOrganizationsAPI:
    """Тесты для эндпоинтов организаций"""

    BASE_URL = "/api/organizations"

    def _check_count_orgs(self, response: Response, count: int):
        body = response.json()["organizations"]
        assert len(body) == count
    
    async def test_get_orgs(self, client: AsyncClient):
        """Успешное получение без фильтров"""
        response = await client.get(
            self.BASE_URL,
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == status.HTTP_200_OK

        self._check_count_orgs(response, 5)
    
    async def test_get_orgs_with_filter_building(self, client: AsyncClient):
        """Успешное получение с фильтром по зданию"""
        response = await client.get(
            f"{self.BASE_URL}?building_id=1",
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == status.HTTP_200_OK

        self._check_count_orgs(response, 1)
    
    async def test_get_orgs_with_filter_activity_name(self, client: AsyncClient):
        """Успешное получение с фильтром по деятельности"""
        response = await client.get(
            f"{self.BASE_URL}?activity_name=Еда",
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == status.HTTP_200_OK

        self._check_count_orgs(response, 2)
    
    async def test_get_orgs_with_filter_name(self, client: AsyncClient):
        """Успешное получение с фильтром по названию"""
        response = await client.get(
            f"{self.BASE_URL}?name=Автоцентр \"DrivePro\"",
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == status.HTTP_200_OK

        self._check_count_orgs(response, 1)
    
    async def test_get_orgs_with_filter_radius(self, client: AsyncClient):
        """Успешное получение с фильтром по радиусу"""
        response = await client.get(
            f"{self.BASE_URL}?radius_meters=1000&radius_lat=55.755864&radius_lng=37.617734",
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == status.HTTP_200_OK

        self._check_count_orgs(response, 1)
    
    async def test_get_orgs_with_filter_bbox(self, client: AsyncClient):
        """Успешное получение с фильтром по области"""
        response = await client.get(
            f"{self.BASE_URL}?&min_lat=55.75&min_lon=37.6&max_lat=55.76&max_lon=37.62",
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == status.HTTP_200_OK

        self._check_count_orgs(response, 1)
    
    async def test_get_orgs_wrong_filter_radius(self, client: AsyncClient):
        """
        Получение с неправильным фильтром по радиусу
        Передан только радиус, без координат
        """
        response = await client.get(
            f"{self.BASE_URL}?radius_meters=1000",
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_orgs_wrong_filter_bbox(self, client: AsyncClient):
        """
        Получение с неправильным фильтром по области
        Переданы не все координаты
        """
        response = await client.get(
            f"{self.BASE_URL}?min_lat=55.75&min_lon=37.6&max_lat=55.76",
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_org_by_id(self, client: AsyncClient):
        """Успешное получение по id"""
        response = await client.get(
            f"{self.BASE_URL}/1",
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == status.HTTP_200_OK
    
    async def test_get_org_by_id_not_found(self, client: AsyncClient):
        """Получение по id несуществующей организации"""
        response = await client.get(
            f"{self.BASE_URL}/100",
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_organization_success(self, client: AsyncClient):
        """Успешное создание организации"""
        data = {
            "name": "Новая организация",
            "phones": ["+71234567890"],
            "building_id": 1,
            "activity_ids": [1, 2]
        }
        response = await client.post(
            self.BASE_URL,
            json=data,
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == status.HTTP_201_CREATED

    async def test_create_organization_building_not_found(self, client: AsyncClient):
        """Ошибка создания организации: здание не найдено"""
        data = {
            "name": "Новая организация",
            "phones": ["+71234567890"],
            "building_id": 999,
            "activity_ids": [1]
        }
        response = await client.post(
            self.BASE_URL,
            json=data,
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_create_organization_activity_not_found(self, client: AsyncClient):
        """Ошибка создания организации: вид деятельности не найден"""
        data = {
            "name": "Новая организация",
            "phones": ["+71234567890"],
            "building_id": 1,
            "activity_ids": [999]
        }
        response = await client.post(
            self.BASE_URL,
            json=data,
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_update_organization_success(self, client: AsyncClient):
        """Успешное обновление организации"""
        data = {
            "name": "Обновленная организация"
        }
        response = await client.patch(
            f"{self.BASE_URL}/1",
            json=data,
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_update_organization_not_found(self, client: AsyncClient):
        """Ошибка обновления организации: организация не найдена"""
        data = {
            "name": "Обновленная организация"
        }
        response = await client.patch(
            f"{self.BASE_URL}/999",
            json=data,
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_organization_building_not_found(self, client: AsyncClient):
        """Ошибка обновления организации: здание не найдено"""
        data = {
            "building_id": 999
        }
        response = await client.patch(
            f"{self.BASE_URL}/1",
            json=data,
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_delete_organization_success(self, client: AsyncClient):
        """Успешное удаление организации"""
        response = await client.delete(
            f"{self.BASE_URL}/1",
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_delete_organization_not_found(self, client: AsyncClient):
        """Ошибка удаления организации: организация не найдена"""
        response = await client.delete(
            f"{self.BASE_URL}/999",
            headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
