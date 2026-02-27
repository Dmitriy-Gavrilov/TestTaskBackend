"""DTO для сущности здания"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class BuildingDTO:
    """DTO для сущности здания"""
    id: int
    address: str
    longitude: float
    latitude: float

    def to_dict(self) -> dict[str, Any]:
        """Конвертация DTO в словарь"""
        return {
            "id": self.id,
            "address": self.address,
            "longitude": self.longitude,
            "latitude": self.latitude,
        }