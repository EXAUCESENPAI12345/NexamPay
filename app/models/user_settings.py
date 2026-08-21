from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class UserSettings(TimestampMixin, Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    language: Mapped[str] = mapped_column(String(5), nullable=False, default="fr")
    currency_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    color: Mapped[str] = mapped_column(String(20), nullable=False, default="nexam")
    theme: Mapped[str] = mapped_column(String(20), nullable=False, default="dark")
    bot_notifications_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user = relationship("User", back_populates="settings")
