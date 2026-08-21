from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Country(TimestampMixin, Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)

    code: Mapped[str] = mapped_column(
        String(3), unique=True, nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    region: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )

    currency_code: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("currencies.code", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    flag_code: Mapped[str] = mapped_column(
        String(10), nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )

    users = relationship(
        "User",
        back_populates="country",
    )

    networks = relationship(
        "MobileMoneyNetwork",
        back_populates="country",
        cascade="all, delete-orphan",
    )
