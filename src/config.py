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

class DetectiveSettings(BaseSettings):
    """Settings for Layer 1 Detective nodes."""
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    
    # Global timeout for all external detective operations (FR-008)
    operation_timeout_seconds: int = 60
    
    # Multimodal LLM parameters (FR-011)
    llm_temperature: float = 0.0

class JudicialSettings(BaseSettings):
    """Settings for Layer 2 Judicial nodes."""
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    
    # Judicial LLM parameters (FR-009)
    llm_temperature: float = 0.0

settings = ObservabilitySettings()
detective_settings = DetectiveSettings()
judicial_settings = JudicialSettings()
