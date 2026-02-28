"""Проверка доступа: trial_ends_at, subscription_plan."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from instant_chat_agent.core.models import SubscriptionPlan, Tenant


BLOCK_MESSAGE = (
    "Пробный период закончился. Оформите подписку для продолжения работы. "
    "Обратитесь в поддержку для оформления."
)


async def check_access(session: AsyncSession, tenant_id: UUID) -> bool:
    """
    Проверяет, есть ли у tenant доступ к функционалу.

    Доступ есть, если:
    - trial_ends_at >= now (пробный период активен), ИЛИ
    - subscription_plan == paid (оплаченная подписка)

    Args:
        session: AsyncSession для запроса к БД
        tenant_id: UUID тенанта

    Returns:
        True если доступ есть, False если заблокирован
    """
    result = await session.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        return False

    if tenant.subscription_plan == SubscriptionPlan.paid:
        if tenant.subscription_ends_at and tenant.subscription_ends_at < datetime.now(timezone.utc):
            return False
        return True

    if tenant.subscription_plan == SubscriptionPlan.trial:
        return tenant.trial_ends_at >= datetime.now(timezone.utc)

    return False


def get_block_message() -> str:
    """Возвращает сообщение при блокировке доступа."""
    return BLOCK_MESSAGE


def require_access(check_fn):
    """
    Декоратор для проверки доступа перед вызовом tool.

    Ожидает, что обёрнутая функция принимает session и tenant_id в kwargs.
    """

    async def wrapper(*args, **kwargs):
        session = kwargs.get("session")
        tenant_id = kwargs.get("tenant_id")
        if session and tenant_id:
            has_access = await check_access(session, tenant_id)
            if not has_access:
                return {"success": False, "error": get_block_message()}
        return await check_fn(*args, **kwargs)

    return wrapper
