from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class VirtualCardApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class VirtualCardStatus(str, Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"


class VirtualCardApplication(TimestampMixin, Base):
    __tablename__ = "virtual_card_applications"

    id: Mapped[int] = mapped_column(primary_key=True)

    application_id: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="RESTRICT"),
        nullable=False
    )

    cardholder_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    phone_number: Mapped[str] = mapped_column(
        String(30), nullable=False
    )

    currency_code: Mapped[str] = mapped_column(
        String(10), nullable=False
    )

    status: Mapped[VirtualCardApplicationStatus] = mapped_column(
        String(30),
        nullable=False,
        default=VirtualCardApplicationStatus.PENDING,
        index=True,
    )

    admin_note: Mapped[str | None] = mapped_column(
        String(1000), nullable=True
    )

    rejection_reason: Mapped[str | None] = mapped_column(
        String(1000), nullable=True
    )

    reviewed_by_telegram_id: Mapped[int | None] = mapped_column(
        nullable=True
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        nullable=True
    )

    user = relationship("User", backref="virtual_card_applications")
    country = relationship("Country")


class VirtualCard(TimestampMixin, Base):
    __tablename__ = "virtual_cards"

    id: Mapped[int] = mapped_column(primary_key=True)

    card_id: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )

    application_id: Mapped[int] = mapped_column(
        ForeignKey("virtual_card_applications.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    currency_code: Mapped[str] = mapped_column(
        String(10), nullable=False
    )

    brand: Mapped[str | None] = mapped_column(
        String(30), nullable=True
    )

    masked_number: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )

    last4: Mapped[str | None] = mapped_column(
        String(4), nullable=True
    )

    expiry_month: Mapped[int | None] = mapped_column(
        nullable=True
    )

    expiry_year: Mapped[int | None] = mapped_column(
        nullable=True
    )

    provider_card_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )

    status: Mapped[VirtualCardStatus] = mapped_column(
        String(20),
        nullable=False,
        default=VirtualCardStatus.ACTIVE,
        index=True,
    )

    application = relationship("VirtualCardApplication")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "status",
            name="uq_virtual_cards_user_status",
        ),
    )
