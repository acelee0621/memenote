from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "MemeNote API"
    BASE_URL: str = "http://localhost:8000"
    JWT_SECRET: str = "your-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 30
    DEBUG: bool = False
    
    # PostgreSQL 配置
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "memenote"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    
    # RabbitMQ 配置
    RABBITMQ_HOST: str = "localhost:5672"
    RABBITMQ_USER: str = "user"
    RABBITMQ_PASSWORD: str = "bitnami"
    
    # Redis 配置
    REDIS_HOST: str = "localhost:6379"

    # S3/MinIO 配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minio"
    MINIO_SECRET_KEY: str = "miniosecret"
    MINIO_USE_SSL: bool = False
    MINIO_BUCKET: str = "memenote"

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"), env_file_encoding="utf-8"
    )


@lru_cache()
def get_settings():
    return Settings() # type: ignore[attr-defined]


settings = get_settings()
