from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class OrderDelivery(TimestampMixin, Base):
    __tablename__ = "order_deliveries"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey(
            "orders.id",
            ondelete="RESTRICT",
        ),
        unique=True,
        nullable=False,
        index=True,
    )

    telegram_user_id: Mapped[int] = mapped_column(
        nullable=False,
        index=True,
    )

    delivery_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    message_id: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    delivered_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )