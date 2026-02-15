"""Configuration for MCP server."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database settings
    db_host: str = "postgresql"
    db_port: int = 5432
    db_name: str = "finance"
    db_user: str = "finance_user"
    db_password: str = "finance_password"

    # Server settings
    server_name: str = "personal-finance-mcp"
    server_version: str = "1.0.0"
    log_level: str = "INFO"

    # HTTP server settings
    http_host: str = "0.0.0.0"
    http_port: int = 8081
    transport_mode: str = "http"

    @property
    def database_url(self) -> str:
        """Get PostgreSQL database URL."""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"


settings = Settings()
