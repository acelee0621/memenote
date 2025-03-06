from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "MemeNote API"
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXPIRATION: int = 30
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"), env_file_encoding="utf-8"
    )


@lru_cache()
def get_settings():
    return Settings() # type: ignore[attr-defined]


settings = get_settings()
