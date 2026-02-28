"""Tool: создание tenant и trial."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from instant_chat_agent.core.config import get_settings
from instant_chat_agent.core.models import Tenant, TenantCreateResult
from instant_chat_agent.core.models import SubscriptionPlan


async def create_tenant_and_trial(
    session: AsyncSession,
    telegram_user_id: str,
    email: str | None = None,
) -> TenantCreateResult:
    """
    Создаёт tenant с trial или возвращает существующего.

    Идемпотентно: при повторном вызове для того же telegram_user_id
    возвращает существующего tenant.
    """
    settings = get_settings()

    # Проверяем существование
    result = await session.execute(
        select(Tenant).where(Tenant.telegram_user_id == telegram_user_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        return TenantCreateResult(
            success=True,
            tenant_id=str(existing.id),
            error=None,
        )

    trial_ends_at = datetime.now(timezone.utc) + timedelta(days=settings.trial_days)
    tenant = Tenant(
        telegram_user_id=telegram_user_id,
        email=email,
        subscription_plan=SubscriptionPlan.trial,
        trial_ends_at=trial_ends_at,
        subscription_ends_at=None,
    )
    session.add(tenant)
    await session.flush()
    await session.refresh(tenant)

    return TenantCreateResult(
        success=True,
        tenant_id=str(tenant.id),
        error=None,
    )


async def get_or_create_tenant(
    session: AsyncSession,
    telegram_user_id: str,
    email: str | None = None,
) -> Tenant | None:
    """
    Получает tenant по telegram_user_id или создаёт с trial.

    Возвращает Tenant или None при ошибке.
    """
    result = await create_tenant_and_trial(session, telegram_user_id, email)
    if not result.success or not result.tenant_id:
        return None

    db_result = await session.execute(select(Tenant).where(Tenant.id == UUID(result.tenant_id)))
    return db_result.scalar_one_or_none()
