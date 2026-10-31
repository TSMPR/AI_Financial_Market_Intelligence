from dataclasses import dataclass
import os
from dotenv import load_dotenv

@dataclass(frozen=True)
class Settings:
    app_name: str = "AI Financial Market Intelligence"
    news_timeout_seconds: int = 15
    news_max_age_days: int = 14
    log_level: str = "INFO"

    @classmethod
    def from_env(cls):
        load_dotenv()
        return cls(
            app_name=os.getenv("APP_NAME", "AI Financial Market Intelligence"),
            news_timeout_seconds=int(os.getenv("NEWS_TIMEOUT_SECONDS", "15")),
            news_max_age_days=int(os.getenv("NEWS_MAX_AGE_DAYS", "14")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
