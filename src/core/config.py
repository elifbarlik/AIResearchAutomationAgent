"""
Configuration management using Pydantic settings.

This module handles loading and validating configuration from environment variables
and .env files.
"""


from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    llm_api_key: str | None = None
    search_api_key: str | None = None
    default_depth: str = "short"
    default_mode: str = "overview"
    gemini_api_key: str | None = None
    tavily_api_key: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Get the application settings singleton.

    This function returns a cached instance of Settings to ensure that
    configuration is only loaded once during the application lifecycle.
    The @lru_cache decorator ensures that subsequent calls return the
    same instance without reloading from the environment.

    Returns:
        Settings: The application settings instance with all configuration values

    Raises:
        ValidationError: If required environment variables are missing or invalid

    Example:
        >>> settings = get_settings()
        >>> print(settings.llm_api_key)
        'your-api-key-here'
    """
    return Settings()
