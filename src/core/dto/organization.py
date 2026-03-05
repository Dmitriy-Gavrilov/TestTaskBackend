"""DTO для сущности организации"""

from dataclasses import dataclass

from src.core.dto.activity import ActivityDTO
from src.core.dto.building import BuildingDTO


@dataclass(frozen=True, slots=True)
class OrganizationDTO:
    """DTO для сущности организации"""
    id: int
    name: str
    phones: list[str]
    activities: list[ActivityDTO]
    building: BuildingDTO

    def to_dict(self) -> dict[str, int | str | list[str] | dict | list[dict]]:
        """Конвертация DTO в словарь"""
        return {
            "id": self.id,
            "name": self.name,
            "phones": self.phones,
            "activities": [a.to_dict() for a in self.activities],
            "building": self.building.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class CreateOrganizationDTO:
    """DTO для создания организации"""
    name: str
    phones: list[str]
    activity_ids: list[int]
    building_id: int


@dataclass(frozen=True, slots=True)
class UpdateOrganizationDTO:
    """DTO для обновления организации"""
    name: str | None
    phones: list[str] | None
    activity_ids: list[int] | None
    building_id: int | None
