"""Модуль взаимодействия с Redis"""

from functools import lru_cache

from pydantic import BaseModel
from redis.asyncio import Redis

from src.settings import redis_settings


class RedisService:
    def __init__(self):
        self.redis_client = Redis(
            host=redis_settings.REDIS_HOST,
            port=redis_settings.REDIS_PORT,
            password=redis_settings.REDIS_PASSWORD,
            decode_responses=True
        )

    async def set_cache(self, key: str, value: BaseModel, ex: int) -> None:
        json_value = value.model_dump_json()
        await self.redis_client.set(f"cache:{key}", json_value, ex=ex)

    async def get_cache(self, key: str, model: type[BaseModel]) -> BaseModel | None:
        value = await self.redis_client.get(f"cache:{key}")
        if value:
            return model.model_validate_json(value)
        return None

    async def del_cache(self, key: str) -> None:
        await self.redis_client.delete(f"cache:{key}")
    
    async def del_cache_pattern(self, pattern: str) -> None:
        """Удалить все ключи по шаблону"""
        keys = await self.redis_client.keys(f"cache:{pattern}")
        if keys:
            await self.redis_client.delete(*keys)


@lru_cache()
def get_redis_service() -> RedisService:
    """Возвращает сервис Redis с ленивой инициализацией"""
    return RedisService()