"""Configuration settings for ETL Service."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "Finance ETL Service"
    debug: bool = False

    # Database
    database_url: str = "postgresql://finance_user:finance_dev_password_change_me@postgres:5432/finance_db"

    # File Upload
    upload_dir: str = "/tmp/uploads"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: list[str] = [".csv"]

    # CSV Processing
    default_encoding: str = "utf-8"
    encoding_fallbacks: list[str] = ["latin-1", "cp1252", "iso-8859-1"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
