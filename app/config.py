from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NexamPay"
    app_env: str = "production"
    debug: bool = False

    secret_key: str = Field(min_length=32)
    jwt_secret_key: str = Field(min_length=32)

    database_url: str

    telegram_bot_token: str
    telegram_bot_username: str

    mobile_fusion_api_url: str | None = None
    mobile_fusion_api_key: str | None = None
    mobile_fusion_secret_key: str | None = None

    admin_telegram_id: int | None = None
    admin_access_code: str | None = None

    default_transaction_timeout_seconds: int = 900

    fee_free_limit: int = 1500
    fee_percent: int = 5

    min_transaction_amount: int = 1
    max_transaction_amount: int = 100_000_000

    cors_origins: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()