from sqlalchemy import BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
        nullable=False,
    )

    telegram_username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    first_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    last_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    photo_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    pin_hash: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
    )

    nexampay_id: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        index=True,
        nullable=False,
    )

    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id"),
        nullable=False,
        index=True,
    )

    network_id: Mapped[int | None] = mapped_column(
        ForeignKey("mobile_money_networks.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


    country = relationship(
        "Country",
        back_populates="users",
    )

    wallets = relationship(
        "Wallet",
        back_populates="user",
        cascade="all, delete-orphan",
    )