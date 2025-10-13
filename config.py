"""
Configuration management for the AI Ticket Booking System.
Loads environment variables and provides centralized configuration access.
"""

from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"

    # Amadeus API Configuration
    amadeus_api_key: str
    amadeus_api_secret: str
    amadeus_hostname: Literal["test", "production"] = "test"

    # Application Configuration
    log_level: str = "INFO"
    environment: Literal["development", "production"] = "development"
    
    # Currency Configuration
    local_currency: str = "USD"  # User's preferred currency (USD, EUR, GBP, INR, etc.)
    enable_currency_conversion: bool = True  # Enable automatic currency conversion
    exchange_rate_api_url: str = "https://open.er-api.com/v6/latest"  # Exchange rate API base URL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
