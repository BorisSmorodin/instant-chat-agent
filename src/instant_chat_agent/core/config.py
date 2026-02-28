"""Конфигурация приложения."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database (postgresql:// or postgresql+asyncpg://)
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/instant_chat"

    # Redis (сессии, очереди)
    redis_url: str = "redis://localhost:6379/0"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None

    # LLM
    gigachat_api_key: str | None = None
    yandex_gpt_api_key: str | None = None

    # Telegram (бот продукта)
    product_bot_token: str = ""

    # Оркестратор контейнеров
    docker_socket: str = "unix:///var/run/docker.sock"
    bot_image: str = "instant-chat-agent-bot:latest"

    # Trial
    trial_days: int = 5


_settings: Settings | None = None


def get_settings() -> Settings:
    """Возвращает синглтон настроек."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
