from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent

POSTGRES_PASSWORD = ''
POSTGRES_USER = ''
POSTGRES_DB = ''
POSTGRES_HOST = ''
POSTGRES_PORT = ''

class Settings(BaseSettings):
    db_url: str = f"sqlite+aiosqlite:///{BASE_DIR}/database.db"
    # db_url: str = f'postgresql+asyncpg://{POSTEGRES_USER}:{POSTEGRES_PASSWORD}@{POSTEGRES_HOST}:{POSTEGRES_PORT}/{POSTEGRES_DB}'
    echo: bool = False


settings = Settings()
