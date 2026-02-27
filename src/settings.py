"""Настройки приложения"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Класс настроек базы данных"""

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def get_db_url(self) -> str:
        """Возвращает URL для подключения к базе данных"""
        return (
            f"postgresql+asyncpg://{self.DB_USER}:"
            f"{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )



class AppSettings(BaseSettings):
    """Класс настроек приложения"""

    API_KEY: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_db_settings() -> DatabaseSettings:
    """Возвращает настройки базы данных с ленивой инициализацией"""
    return DatabaseSettings()


@lru_cache()
def get_app_settings() -> AppSettings:
    """Возвращает настройки приложения с ленивой инициализацией"""
    return AppSettings()


db_settings = get_db_settings()
app_settings = get_app_settings()
