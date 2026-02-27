"""Зависимости для API"""

from fastapi import HTTPException, status, Depends
from fastapi.security import APIKeyHeader

from src.settings import app_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def check_api_key(api_key: str = Depends(api_key_header)) -> None:
    """Проверка API ключа"""
    if api_key != app_settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный API-ключ")
