from decimal import Decimal
from enum import Enum

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class DepositStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DepositRequest(TimestampMixin, Base):
    __tablename__ = "deposit_requests"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    deposit_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    country_id: Mapped[int] = mapped_column(
        ForeignKey(
            "countries.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    network_id: Mapped[int] = mapped_column(
        ForeignKey(
            "mobile_money_networks.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    phone_number: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=False,
    )

    fee: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=False,
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=False,
    )

    currency_code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    status: Mapped[DepositStatus] = mapped_column(
        String(30),
        nullable=False,
        default=DepositStatus.PENDING,
        index=True,
    )

    provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    provider_transaction_id: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    failure_reason: Mapped[
        str | None
    ] = mapped_column(
        String(500),
        nullable=True,
    )