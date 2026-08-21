from decimal import Decimal
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ExchangeRate(TimestampMixin, Base):
    __tablename__ = "exchange_rates"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    from_currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )

    to_currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )

    rate: Mapped[Decimal] = mapped_column(
        Numeric(30, 12),
        nullable=False,
    )

    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    valid_until: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
        index=True,
    )