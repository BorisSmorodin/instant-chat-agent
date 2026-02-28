# Прогресс разработки

Документ фиксирует выполненную работу. Используйте его, чтобы не возвращаться к уже реализованным задачам.

---

## Фаза 0: Инфраструктура — ВЫПОЛНЕНО

**Дата завершения:** 2025-02-28  
**Оценка:** 13 SP

### F0-1. Модели БД — выполнено

**Файл:** `src/instant_chat_agent/core/models.py`

- SQLAlchemy `Base`, declarative base
- Модели: `Tenant`, `Bot`, `BotConfig`, `Document`, `LlmUsage`, `AgentTrace`, `Session`
- Enums: `SubscriptionPlan` (trial/paid/cancelled), `BotStatus` (pending/active/suspended/error)
- Pydantic-схемы: `TenantCreate`, `TenantCreateResult`, `BotCreate`, `BotListItem`
- Связи: Tenant → bots, Bot → config, Bot → documents

**Не требуется:** повторная реализация моделей.

---

### F0-2. Подключение к БД — выполнено

**Файлы:** `src/instant_chat_agent/core/database.py`, `src/instant_chat_agent/core/config.py`

- Async engine (`postgresql+asyncpg://`), автопреобразование `postgresql://`
- `AsyncSessionLocal` с `expire_on_commit=False`
- `get_db()` — async generator для FastAPI/DI
- `DatabaseSession` — контекстный менеджер
- `init_db()`, `dispose_db()` — инициализация и shutdown
- `get_settings()` — синглтон настроек

**Не требуется:** повторная настройка подключения к БД.

---

### F0-3. Миграции — выполнено

**Файл:** `scripts/migrate_db.py`

- Создание всех таблиц через `Base.metadata.create_all`
- Индексы: `ix_llm_usage_created_at`, `ix_agent_traces_created_at`
- Запуск: `python scripts/migrate_db.py`

**Зависимость:** PostgreSQL должен быть запущен (`docker compose -f docker/compose.yml up -d`).

**Не требуется:** повторное создание миграций для текущей схемы.

---

### F0-4. create_tenant_and_trial — выполнено

**Файл:** `src/instant_chat_agent/tools/tenant.py`

- `create_tenant_and_trial(session, telegram_user_id, email?)` — идемпотентно создаёт tenant с trial
- `get_or_create_tenant(session, telegram_user_id, email?)` — получение или создание
- Возврат: `TenantCreateResult(success, tenant_id, error)`
- `trial_ends_at = now + settings.trial_days`

**Не требуется:** повторная реализация tenant/trial.

---

### F0-5. Оркестратор контейнеров — выполнено

**Файл:** `src/instant_chat_agent/orchestrator/docker.py`

- `ContainerOrchestrator`: `create_container()`, `stop_container()`, `is_container_running()`
- Функции: `create_container(bot_id, token, qdrant_url?)`, `stop_container(container_id)`
- Env в контейнере: `BOT_TOKEN`, `BOT_ID`, `QDRANT_URL`
- Ограничения: `mem_limit=512m`, `restart_policy=on-failure`
- Токен передаётся уже расшифрованным (расшифровка — в вызывающем коде)

**Не требуется:** повторная реализация оркестратора.

---

### F0-6. Проверка доступа — выполнено

**Файл:** `src/instant_chat_agent/subscription/access.py`

- `check_access(session, tenant_id)` — проверка trial/subscription
- `get_block_message()` — текст при блокировке
- Декоратор `require_access` — проверка перед вызовом tool (ожидает `session`, `tenant_id` в kwargs)
- Логика: trial_ends_at >= now ИЛИ subscription_plan == paid (с учётом subscription_ends_at)

**Не требуется:** повторная реализация проверки доступа.

---

## Чек-лист готовности Фазы 0

- [x] Все таблицы созданы и миграции применяются
- [x] `create_tenant_and_trial` создаёт tenant с trial
- [x] Оркестратор создаёт/останавливает контейнер с образом bot
- [x] `check_access` возвращает корректный результат
- [x] `docker compose up` поднимает PostgreSQL, Redis, Qdrant
- [x] `pip install -e .` + `python scripts/migrate_db.py` работают (при запущенной БД)

---

## Следующие фазы (не начаты)

| Фаза | Описание | Оценка |
|------|----------|--------|
| 1 | Агент-помощник: LangGraph, Telegram, tools | 13 SP |
| 2 | Регистрация бота: token, контейнер, клиентский бот | 13 SP |
| 3 | RAG: загрузка документа, Qdrant, интеграция в агента | 13 SP |
| 4 | Кастомизация: system prompt через диалог | 5 SP |
| 5 | Мониторинг: метрики, отчёт для агента | 8 SP |
| 6 | Дашборд: трейсы, логи, UI | 8 SP |
| 7 | Оплата и продление | 5 SP |

---

## Быстрая проверка

```bash
# 1. Инфраструктура
docker compose -f docker/compose.yml up -d

# 2. Миграции
python scripts/migrate_db.py

# 3. Проверка импортов
python -c "
from instant_chat_agent.core.models import Tenant, Bot
from instant_chat_agent.tools.tenant import create_tenant_and_trial
from instant_chat_agent.subscription.access import check_access, get_block_message
from instant_chat_agent.orchestrator.docker import create_container, stop_container
print('OK')
"
```
