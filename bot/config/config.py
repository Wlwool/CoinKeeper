import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class Config:
    BOT_TOKEN: str = os.environ.get("BOT_TOKEN")
    DB_URL: str = os.environ.get("DB_URL")
    ADMIN_IDS: list = None

    # Redis
    USE_REDIS: bool = os.environ.get("USE_REDIS", "false").lower() == "true"
    REDIS_HOST: str = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.environ.get("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.environ.get("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.environ.get("REDIS_PASSWORD", "")

    # База данных
    # DB_URL: str = os.environ.get("DB_URL", "sqlite+aiosqlite:///./bot.db")

    def __post_init__(self):
        admin_ids = os.environ.get("ADMIN_IDS", "")
        self.ADMIN_IDS = [int(admin_id) for admin_id in admin_ids.split(",") if
                          admin_id] if admin_ids else []

        # Валидация обязательных параметров
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required!")
