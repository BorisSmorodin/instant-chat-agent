#!/usr/bin/env python3
"""Миграции БД: создание таблиц."""

import asyncio
import sys
from pathlib import Path

# Добавляем корень проекта в path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from instant_chat_agent.core.config import get_settings
from instant_chat_agent.core.models import Base


def _get_async_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


async def migrate() -> None:
    """Создание всех таблиц."""
    settings = get_settings()
    url = _get_async_url(settings.database_url)
    engine = create_async_engine(url, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Индексы для производительности (опционально)
        for index_sql in [
            "CREATE INDEX IF NOT EXISTS ix_llm_usage_created_at ON llm_usage (created_at)",
            "CREATE INDEX IF NOT EXISTS ix_agent_traces_created_at ON agent_traces (created_at)",
        ]:
            try:
                await conn.execute(text(index_sql))
            except Exception as e:
                print(f"Предупреждение: индекс не создан ({e})")

    await engine.dispose()
    print("Миграции применены успешно.")


if __name__ == "__main__":
    asyncio.run(migrate())
