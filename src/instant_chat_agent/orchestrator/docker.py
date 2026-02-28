"""Docker-оркестратор: создание, конфигурация, остановка контейнеров."""

import logging
from uuid import UUID

import docker
from docker.errors import DockerException

from instant_chat_agent.core.config import get_settings

logger = logging.getLogger(__name__)


class ContainerOrchestrator:
    """Оркестратор Docker-контейнеров для клиентских ботов."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = docker.from_env()
        self._image = settings.bot_image
        self._qdrant_url = settings.qdrant_url

    def create_container(
        self,
        bot_id: UUID,
        token: str,
        qdrant_url: str | None = None,
    ) -> str:
        """
        Создаёт и запускает контейнер бота.

        Args:
            bot_id: UUID бота
            token: Расшифрованный Telegram bot token
            qdrant_url: URL Qdrant (по умолчанию из настроек)

        Returns:
            container_id контейнера

        Raises:
            DockerException: при ошибке создания/запуска
        """
        url = qdrant_url or self._qdrant_url
        env = {
            "BOT_TOKEN": token,
            "BOT_ID": str(bot_id),
            "QDRANT_URL": url,
        }

        try:
            container = self._client.containers.run(
                self._image,
                detach=True,
                environment=env,
                name=f"instant-chat-bot-{bot_id}",
                restart_policy={"Name": "on-failure", "MaximumRetryCount": 3},
                mem_limit="512m",
                network_mode="bridge",
            )
            if hasattr(container, "id"):
                container_id = container.id
            else:
                container_id = str(container)
            logger.info("Создан контейнер %s для бота %s", container_id, bot_id)
            return container_id
        except DockerException as e:
            logger.exception("Ошибка создания контейнера для бота %s: %s", bot_id, e)
            raise

    def stop_container(self, container_id: str) -> None:
        """
        Останавливает и удаляет контейнер.

        Args:
            container_id: ID контейнера
        """
        try:
            container = self._client.containers.get(container_id)
            container.stop(timeout=10)
            container.remove()
            logger.info("Остановлен и удалён контейнер %s", container_id)
        except DockerException as e:
            logger.warning("Ошибка остановки контейнера %s: %s", container_id, e)

    def is_container_running(self, container_id: str) -> bool:
        """Проверяет, запущен ли контейнер."""
        try:
            container = self._client.containers.get(container_id)
            return container.status == "running"
        except DockerException:
            return False


def create_container(
    bot_id: UUID,
    token: str,
    qdrant_url: str | None = None,
) -> str:
    """
    Удобная функция для создания контейнера.

    Returns:
        container_id
    """
    orchestrator = ContainerOrchestrator()
    return orchestrator.create_container(bot_id, token, qdrant_url)


def stop_container(container_id: str) -> None:
    """Удобная функция для остановки контейнера."""
    orchestrator = ContainerOrchestrator()
    orchestrator.stop_container(container_id)
