# Instant Chat Agent

Платформа для создания и кастомизации RAG-ботов в Telegram. Интерфейс на естественном языке: пользователь общается с агентом-помощником, который создаёт и настраивает ботов под его нужды.

## Стек

- **Агенты:** LangChain + LangGraph
- **RAG:** Qdrant
- **LLM:** GigaChat, YandexGPT

## Структура проекта

- [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) — структура каталогов
- [docs/DECOMPOSITION.md](docs/DECOMPOSITION.md) — декомпозиция и детализация
- [docs/PROGRESS.md](docs/PROGRESS.md) — выполненные задачи, прогресс по фазам

## Быстрый старт

```bash
# Инфраструктура (PostgreSQL, Redis, Qdrant)
docker compose -f docker/compose.yml up -d

# Установка
pip install -e .

# Конфигурация
cp config/settings.example.env .env
# Заполнить .env (PRODUCT_BOT_TOKEN, API keys)

# Миграции
python scripts/migrate_db.py

# Запуск бота продукта
python -m instant_chat_agent.main
```
