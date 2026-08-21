from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class TransferStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Transfer(TimestampMixin, Base):
    __tablename__ = "transfers"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    transfer_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    transaction_id: Mapped[int] = mapped_column(
        ForeignKey(
            "transactions.id",
            ondelete="RESTRICT",
        ),
        unique=True,
        nullable=False,
    )
     
    idempotency_key: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    sender_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    receiver_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    sender_currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    receiver_currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    amount_sent: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=False,
    )

    fee: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=False,
    )

    total_debited: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=False,
    )

    exchange_rate: Mapped[Decimal] = mapped_column(
        Numeric(30, 12),
        nullable=False,
    )

    amount_received: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=False,
    )

    status: Mapped[TransferStatus] = mapped_column(
        String(30),
        nullable=False,
        default=TransferStatus.PENDING,
        index=True,
    )