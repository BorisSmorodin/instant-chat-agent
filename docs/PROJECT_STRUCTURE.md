# Структура проекта

```
instant-chat-agent/
├── config/                    # Конфигурация
│   └── settings.example.env   # Пример .env
├── docker/
│   ├── Dockerfile.product     # Образ бота продукта
│   ├── Dockerfile.bot         # Образ клиентского RAG-бота
│   └── compose.yml            # PostgreSQL, Redis, Qdrant
├── docs/
│   ├── DECOMPOSITION.md       # Декомпозиция и детализация
│   └── PROJECT_STRUCTURE.md   # Этот файл
├── scripts/
│   ├── run_product_bot.py     # Запуск бота продукта
│   └── migrate_db.py          # Миграции БД
├── src/
│   └── instant_chat_agent/
│       ├── __init__.py
│       ├── main.py            # Точка входа продукта
│       ├── agent/             # Агент-помощник (LangGraph)
│       │   ├── graph.py       # Граф с нодами
│       │   └── nodes.py       # router, register_bot, upload_document, ...
│       ├── bot/               # Клиентский RAG-бот (в контейнере)
│       │   ├── main.py        # Точка входа бота
│       │   └── graph.py       # retrieve -> generate -> respond
│       ├── dashboard/          # Веб-дашборд (Фаза 6)
│       │   └── app.py
│       ├── core/              # Общее
│       │   ├── config.py      # Settings
│       │   ├── models.py      # Модели данных
│       │   └── database.py   # Подключение к БД
│       ├── llm/               # LLM провайдеры
│       │   ├── base.py
│       │   ├── gigachat.py
│       │   └── yandex_gpt.py
│       ├── monitoring/        # Метрики, трейсы
│       │   ├── metrics.py
│       │   └── traces.py
│       ├── orchestrator/      # Оркестратор контейнеров
│       │   └── docker.py
│       ├── rag/               # RAG (Qdrant)
│       │   ├── qdrant_store.py
│       │   ├── indexing.py
│       │   └── retriever.py
│       ├── session/           # Контекст сессии
│       │   └── store.py
│       ├── subscription/      # Подписка, trial
│       │   └── access.py
│       ├── telegram/          # Telegram
│       │   ├── product_bot.py
│       │   └── handlers.py
│       └── tools/             # Tools агента
│           ├── register_bot.py
│           ├── list_bots.py
│           ├── upload_document.py
│           ├── update_prompt.py
│           ├── get_report.py
│           └── tenant.py
├── tests/
│   ├── conftest.py
│   ├── test_agent/
│   └── test_tools/
├── pyproject.toml
└── README.md
```

## Запуск

1. **Инфраструктура:** `docker compose -f docker/compose.yml up -d`
2. **Миграции:** `python scripts/migrate_db.py`
3. **Бот продукта:** `python -m instant_chat_agent.main` или `instant-chat-product`

## Сборка образов

- `docker build -f docker/Dockerfile.product -t instant-chat-agent-product .`
- `docker build -f docker/Dockerfile.bot -t instant-chat-agent-bot .`
