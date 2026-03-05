"""Схемы для работы с организациями"""

from typing import Annotated
from pydantic import BaseModel, Field, field_validator, model_validator


PhoneStr = Annotated[str, Field(pattern=r'^\+?[1-9]\d{7,14}$')]
ActivityStr = Annotated[str, Field(min_length=1, max_length=255)]


class OrganizationFilters(BaseModel):
    """Фильтры для поиска организаций"""
    
    building_id: int | None = Field(default=None, description="ID здания")
    activity_name: str | None = Field(default=None, description="Название вида деятельности")
    name: str | None = Field(default=None, description="Поиск по названию организации")
    
    # Географические фильтры
    radius_lat: float | None = Field(default=None, description="Широта центра для радиусного поиска")
    radius_lng: float | None = Field(default=None, description="Долгота центра для радиусного поиска")
    radius_meters: float | None = Field(default=None, description="Радиус в метрах для поиска организаций")
    
    # Для прямоугольной области
    min_lat: float | None = Field(default=None, description="Широта юго-западного угла области")
    min_lon: float | None = Field(default=None, description="Долгота юго-западного угла области")
    max_lat: float | None = Field(default=None, description="Широта северо-восточного угла области")
    max_lon: float | None = Field(default=None, description="Долгота северо-восточного угла области")

    @model_validator(mode="before")
    def check_geography(
        cls,
        values: dict[str, int | float | str | None]
    ) -> dict[str, int | float | str | None]:
        # Радиус
        radius_fields = [values.get("radius_lat"), values.get("radius_lng"), values.get("radius_meters")]
        if any(f is not None for f in radius_fields) and not all(f is not None for f in radius_fields):
            raise ValueError(
                "Для поиска по радиусу нужно передать все три параметра: radius_lat, radius_lng, radius_meters"
            )
        
        # Bounding box
        bbox_fields = [values.get("min_lat"), values.get("min_lon"), values.get("max_lat"), values.get("max_lon")]
        if any(f is not None for f in bbox_fields) and not all(f is not None for f in bbox_fields):
            raise ValueError(
                "Для поиска по области нужно передать все четыре параметра: min_lat, min_lon, max_lat, max_lon"
            )
        
        return values


class BaseOrganizationSchema(BaseModel):
    """Базовая схема для данных организации"""
    name: str = Field(..., description="Название организации", min_length=1, max_length=255)
    phones: list[PhoneStr] = Field(..., description="Список телефонов организации")


class BuildingSchema(BaseModel):
    """Схема для данных здания"""
    id: int = Field(..., description="ID здания")
    address: str = Field(..., description="Адрес здания")
    longitude: float = Field(..., description="Долгота здания")
    latitude: float = Field(..., description="Широта здания")


class OrganizationSchema(BaseOrganizationSchema):
    """Схема для данных организации"""
    id: int = Field(..., description="ID организации")
    building: BuildingSchema = Field(..., description="Данные здания")
    activities: list[ActivityStr] = Field(..., description="Список видов деятельности")


class GetOrganizationResponse(BaseModel):
    """Ответ с информацией об организации по ID"""
    organization: OrganizationSchema


class GetOrganizationsResponse(BaseModel):
    """Ответ с информацией об организациях"""
    organizations: list[OrganizationSchema]


class CreateOrganizationRequest(BaseOrganizationSchema):
    """Запрос на создание организации"""
    building_id: int = Field(..., description="ID здания")
    activity_ids: list[int] = Field(..., description="Список ID видов деятельности")

    @field_validator("phones", mode="before")
    def unique_phones(cls, v: list[str]) -> list[str]:
        return list(set(v))


class CreateOrganizationResponse(BaseModel):
    """Ответ на создание организации"""
    id: int = Field(..., description="ID созданной организации")


class UpdateOrganizationRequest(BaseModel):
    """Запрос на обновление организации"""
    name: str | None = Field(
        None, description="Название организации", min_length=1, max_length=255)
    phones: list[PhoneStr] | None = Field(None, description="Список телефонов организации")
    building_id: int | None = Field(None, description="ID здания")
    activity_ids: list[int] | None = Field(None, description="Список ID видов деятельности")

    @field_validator("phones", mode="before")
    def unique_phones(cls, v: list[str]) -> list[str]:
        return list(set(v))


