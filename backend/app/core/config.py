"""Core configuration for ContractCopilot backend."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # Application settings
    app_name: str = "ContractCopilot"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    # API settings
    api_v1_prefix: str = "/api/v1"

    # CORS settings
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    # File processing settings
    upload_dir: str = "./uploads"  # Relative to project root, not /tmp
    max_file_size: int = 50 * 1024 * 1024  # 50MB in bytes
    allowed_file_types: list[str] = ["pdf", "docx", "txt"]
    file_cleanup_interval: int = 3600  # 1 hour in seconds
    auto_cleanup_after_analysis: bool = False  # Clean up files after analysis completes

    # OpenAI settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"  # Using gpt-3.5-turbo for better rate limits
    openai_max_tokens: int = 1000  # Reduced to fit within rate limits
    openai_temperature: float = 0.1

    # Langfuse settings (for future use)
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    langfuse_host: str = "https://cloud.langfuse.com"


# Global settings instance
settings = Settings()
