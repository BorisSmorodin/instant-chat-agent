"""Модели данных (SQLAlchemy + Pydantic)."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base для SQLAlchemy моделей."""

    pass


class SubscriptionPlan(str, Enum):
    """План подписки."""

    trial = "trial"
    paid = "paid"
    cancelled = "cancelled"


class BotStatus(str, Enum):
    """Статус бота."""

    pending = "pending"
    active = "active"
    suspended = "suspended"
    error = "error"


def _uuid4() -> UUID:
    return uuid4()


# --- SQLAlchemy models ---


class Tenant(Base):
    """Клиент (тенант)."""

    __tablename__ = "tenants"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=_uuid4)
    telegram_user_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(256), nullable=True)
    subscription_plan: Mapped[SubscriptionPlan] = mapped_column(
        SQLEnum(SubscriptionPlan), default=SubscriptionPlan.trial, nullable=False
    )
    trial_ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    subscription_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    bots = relationship("Bot", back_populates="tenant", cascade="all, delete-orphan")


class Bot(Base):
    """Бот клиента."""

    __tablename__ = "bots"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=_uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    telegram_bot_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    container_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[BotStatus] = mapped_column(
        SQLEnum(BotStatus), default=BotStatus.pending, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="bots")
    config = relationship("BotConfig", back_populates="bot", uselist=False, cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="bot", cascade="all, delete-orphan")


class BotConfig(Base):
    """Конфигурация бота."""

    __tablename__ = "bot_configs"

    bot_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("bots.id", ondelete="CASCADE"), primary_key=True
    )
    system_prompt: Mapped[str] = mapped_column(Text, default="", nullable=False)
    model_id: Mapped[str] = mapped_column(String(64), default="gigachat", nullable=False)
    temperature: Mapped[float] = mapped_column(default=0.7, nullable=False)
    scenario_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    bot = relationship("Bot", back_populates="config")


class Document(Base):
    """Документ базы знаний бота."""

    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=_uuid4)
    bot_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("bots.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_name: Mapped[str] = mapped_column(String(256), nullable=False)
    chunks_count: Mapped[int] = mapped_column(default=0, nullable=False)
    indexed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    bot = relationship("Bot", back_populates="documents")


class LlmUsage(Base):
    """Запись об использовании LLM."""

    __tablename__ = "llm_usage"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=_uuid4)
    bot_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("bots.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    request_id: Mapped[str] = mapped_column(String(64), nullable=True, index=True)
    model: Mapped[str] = mapped_column(String(64), nullable=False)
    input_tokens: Mapped[int] = mapped_column(default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(default=0, nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 6), default=Decimal("0"), nullable=False)
    latency_ms: Mapped[int] = mapped_column(default=0, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class AgentTrace(Base):
    """Трейс выполнения агента."""

    __tablename__ = "agent_traces"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=_uuid4)
    bot_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("bots.id", ondelete="CASCADE"), nullable=False, index=True
    )
    trace_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    steps_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class Session(Base):
    """Сессия пользователя (контекст диалога)."""

    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=_uuid4)
    telegram_user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    tenant_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True, index=True
    )
    state_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# --- Pydantic schemas ---


class TenantCreate(BaseModel):
    """Схема создания tenant."""

    telegram_user_id: str
    email: str | None = None


class TenantCreateResult(BaseModel):
    """Результат создания tenant."""

    success: bool
    tenant_id: str | None = None
    error: str | None = None


class BotCreate(BaseModel):
    """Схема создания бота."""

    tenant_id: UUID
    telegram_bot_id: str
    token_encrypted: str


class BotListItem(BaseModel):
    """Элемент списка ботов."""

    bot_id: str
    name: str
    status: str
    created_at: datetime
