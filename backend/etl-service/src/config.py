"""Configuration settings for ETL Service."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "Finance ETL Service"
    debug: bool = False

    # CORS Configuration
    cors_allowed_origins: str = "http://localhost:3000,http://localhost:5173,https://finance.localtest.me:8443"

    # Keycloak OAuth2/OIDC Configuration
    keycloak_server_url: str = "https://keycloak.localtest.me:8443"
    keycloak_realm: str = "master"
    keycloak_client_id: str = "finance-etl"

    # Authentication
    auth_enabled: bool = True
    # Public endpoints that don't require authentication
    public_endpoints: list[str] = ["/", "/api/health", "/docs", "/redoc", "/openapi.json"]

    # Database
    # SECURITY: No default credentials - must be provided via environment variable
    database_url: str

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
