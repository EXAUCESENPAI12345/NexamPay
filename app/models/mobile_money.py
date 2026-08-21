from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class MobileMoneyNetwork(TimestampMixin, Base):
    __tablename__ = "mobile_money_networks"

    id: Mapped[int] = mapped_column(primary_key=True)

    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    logo_url: Mapped[str | None] = mapped_column(
        String(1000), nullable=True
    )

    currency_code: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("currencies.code", ondelete="RESTRICT"),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )

    country = relationship(
        "Country",
        back_populates="networks",
    )
