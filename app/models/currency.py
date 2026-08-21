from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Currency(TimestampMixin, Base):
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    code: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    symbol: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    decimals: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=2,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )