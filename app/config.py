import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "FitBuddy")

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

    gemini_pro_model: str = os.getenv(
        "GEMINI_PRO_MODEL",
        "gemini-3.1-pro-preview",
    )

    gemini_flash_model: str = os.getenv(
        "GEMINI_FLASH_MODEL",
        "gemini-3.8-flash",
    )

    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./fitbuddy.db",
    )

    admin_token: str = os.getenv(
        "ADMIN_TOKEN",
        "",
    )

    debug: bool = os.getenv(
        "DEBUG",
        "true",
    ).lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


settings = Settings()