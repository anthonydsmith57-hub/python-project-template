"""Application configuration and environment variable validation."""

from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Typed application settings loaded from environment variables or a .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    data_input_dir: Path = Field(default=Path("./data/input"))
    data_output_dir: Path = Field(default=Path("./data/output"))
    log_file_path: Path = Field(default=Path("./logs/application.log"))

    api_base_url: str = Field(default="https://example.com")
    api_key: SecretStr = Field(..., min_length=1)
    database_url: SecretStr = Field(..., min_length=1)


def load_configuration() -> AppConfig:
    """Load and validate application configuration from the environment.

    Returns:
        A validated AppConfig instance.

    Raises:
        pydantic.ValidationError: If required variables are missing or invalid.
    """
    return AppConfig()
