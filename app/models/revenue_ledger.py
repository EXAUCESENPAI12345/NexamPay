from decimal import Decimal
from enum import Enum

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class RevenueType(str, Enum):
    DEPOSIT_FEE = "deposit_fee"
    WITHDRAWAL_FEE = "withdrawal_fee"
    TRANSFER_FEE = "transfer_fee"
    PRODUCT_SALE = "product_sale"


class RevenueStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    REVERSED = "reversed"


class RevenueLedger(TimestampMixin, Base):
    __tablename__ = "revenue_ledger"

    id: Mapped[int] = mapped_column(primary_key=True)

    revenue_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    revenue_type: Mapped[RevenueType] = mapped_column(
        String(40),
        nullable=False,
        index=True,
    )

    status: Mapped[RevenueStatus] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=False,
    )

    currency_code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )

    source_transaction_id: Mapped[int | None] = mapped_column(
        ForeignKey("transactions.id"),
        nullable=True,
        index=True,
    )

    source_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders.id"),
        nullable=True,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )