"""Конфигурация приложения."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "postgresql://user:pass@localhost:5432/instant_chat"

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
