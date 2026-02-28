"""
Configuration management for the Digital Courtroom.
Uses Pydantic Settings for environment-based configuration.
"""
from typing import Optional
from pydantic import field_validator
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
    vision_model: str = "gemini-2.0-flash"


class JudicialSettings(BaseSettings):
    """Settings for Layer 2 Judicial nodes."""
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Judicial LLM parameters
    llm_temperature: float = 0.0
    gemini_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # Model Selection
    prosecutor_model: str = "deepseek-v3.1:671b-cloud"
    defense_model: str = "deepseek-v3.1:671b-cloud"
    techlead_model: str = "deepseek-v3.1:671b-cloud"

    # --- Bounded Concurrency Settings (012-bounded-agent-eval) ---
    root_node: Optional[str] = None

    # FR-001: Global semaphore limit for active LLM requests (range 1–50)
    max_concurrent_llm_calls: int = 5


    # FR-002: Retry / Exponential Backoff
    retry_initial_delay: float = 1.0
    retry_max_delay: float = 60.0
    retry_max_attempts: int = 3

    # FR-008: Per-request timeout for hung calls (seconds)
    llm_call_timeout: float = 120.0
    batch_llm_call_timeout: float = 300.0

    # FR-005: Toggle for structured batching mode
    batching_enabled: bool = False

    @field_validator("max_concurrent_llm_calls")
    @classmethod
    def validate_concurrency_limit(cls, v: int) -> int:
        """FR-001: Reject invalid concurrency limits at startup."""
        if v < 1:
            raise ValueError(
                f"MAX_CONCURRENT_LLM_CALLS must be >= 1, got {v}"
            )
        if v > 50:
            raise ValueError(
                f"MAX_CONCURRENT_LLM_CALLS must be <= 50, got {v}"
            )
        return v


settings = ObservabilitySettings()
detective_settings = DetectiveSettings()
judicial_settings = JudicialSettings()
