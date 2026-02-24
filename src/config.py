"""
Configuration management for the Digital Courtroom.
Uses Pydantic Settings for environment-based configuration.
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class ObservabilitySettings(BaseSettings):
    """Settings for observability and tracing."""
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    
    # LangSmith Tracing
    langchain_tracing_v2: bool = False
    langchain_endpoint: str = "https://api.smith.langchain.com"
    langchain_api_key: Optional[str] = None
    langchain_project: str = "digital-courtroom"
    
    # Redaction
    pii_masking_enabled: bool = True
    
    # LangSmith Performance
    langsmith_timeout: int = 5
    langsmith_retries: int = 3

settings = ObservabilitySettings()
