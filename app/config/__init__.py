from pydantic_settings import BaseSettings

from functools import lru_cache


class Settings(BaseSettings):
    contact_discord: str = ""
    discord_webhook_url: str = ""


@lru_cache()
def settings():
    return Settings()
