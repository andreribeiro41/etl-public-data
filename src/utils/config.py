from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # mapeia variáveis do .env
    city_list: str = Field(default="sao_paulo;rio_de_janeiro;brasilia", alias="CITY_LIST")
    past_days: int = Field(default=3, alias="PAST_DAYS")
    forecast_days: int = Field(default=0, alias="FORECAST_DAYS")
    timezone: str = Field(default="America/Sao_Paulo", alias="TIMEZONE")
    db_uri: str | None = Field(default=None, alias="DB_URI")

    # configuração do Pydantic Settings (v2)
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    def cities(self) -> list[str]:
        return [c.strip() for c in self.city_list.split(";") if c.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()


# from pydantic import BaseSettings, Field
# from functools import lru_cache

# class Settings(BaseSettings):
#     city_list: str = Field(default="sao_paulo;rio_de_janeiro;brasilia", alias="CITY_LIST")
#     past_days: int = Field(default=3, alias="PAST_DAYS")
#     forecast_days: int = Field(default=0, alias="FORECAST_DAYS")
#     timezone: str = Field(default="America/Sao_Paulo", alias="TIMEZONE")
#     db_uri: str | None = Field(default=None, alias="DB_URI")
#     class Config:
#         env_file = ".env"
#         case_sensitive = False
#     def cities(self) -> list[str]:
#         return [c.strip() for c in self.city_list.split(";") if c.strip()]

# @lru_cache
# def get_settings() -> Settings:
#     return Settings()
