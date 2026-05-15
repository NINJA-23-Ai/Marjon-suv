from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils.parsing import parse_int_list


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = Field(..., alias="BOT_TOKEN")
    admin_chat_id: int = Field(..., alias="ADMIN_CHAT_ID")
    admin_ids_raw: str = Field("", alias="ADMIN_IDS")
    database_url: str = Field(..., alias="DATABASE_URL")
    api_host: str = Field("0.0.0.0", alias="API_HOST")
    api_port: int = Field(8000, alias="API_PORT")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    water_19l_price: int = Field(15_000, alias="WATER_19L_PRICE")
    pump_price: int = Field(45_000, alias="PUMP_PRICE")
    empty_bottle_exchange_price: int = Field(0, alias="EMPTY_BOTTLE_EXCHANGE_PRICE")

    @property
    def admin_ids(self) -> list[int]:
        return parse_int_list(self.admin_ids_raw)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
