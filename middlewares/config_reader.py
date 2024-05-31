from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    bot_token: SecretStr
    admin_chat_id: str
    language: str
    throttling: int

    model_config = SettingsConfigDict(env_file=f'{BASE_DIR}/.env', env_file_encoding='utf-8')


config = Settings()#