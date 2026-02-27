"""DTO для сущности деятельности"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ActivityDTO:
    """DTO для сущности деятельности"""
    id: int
    name: str

    def to_dict(self) -> dict[str, int | str]:
        """Конвертация DTO в словарь"""
        return {"id": self.id, "name": self.name}