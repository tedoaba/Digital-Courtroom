import json
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class HardenedConfig(BaseSettings):
    """
    Centralized storage for all swarm configuration derived from environment and vault.
    (013-ironclad-hardening)
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Configurable sets (usually passed as JSON strings in ENV)
    models: dict[str, str] = Field(
        default_factory=dict, validation_alias="COURTROOM_MODELS"
    )
    endpoints: dict[str, str] = Field(
        default_factory=dict, validation_alias="COURTROOM_ENDPOINTS"
    )
    timeouts: dict[str, int] = Field(
        default_factory=dict, validation_alias="COURTROOM_TIMEOUTS"
    )

    # Vault / Security
    vault_key: SecretStr | None = Field(
        default=None, validation_alias="COURTROOM_VAULT_KEY"
    )
    vault_secrets: dict[str, SecretStr] = Field(default_factory=dict)

    @field_validator("models", "endpoints", "timeouts", mode="before")
    @classmethod
    def parse_json_strings(cls, v):
        """Allow JSON string inputs for dict types from environment variables."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v

    @field_validator("models")
    @classmethod
    def validate_models(cls, v: dict[str, str]) -> dict[str, str]:
        """All model names must be non-empty."""
        for name, model_id in v.items():
            if not model_id:
                raise ValueError(f"Model ID for {name} cannot be empty")
        return v

    @field_validator("timeouts")
    @classmethod
    def validate_timeouts(cls, v: dict[str, int]) -> dict[str, int]:
        """Timeouts must be between 1 and 300 seconds."""
        for name, timeout in v.items():
            if not (1 <= timeout <= 300):
                raise ValueError(
                    f"Timeout {name} must be between 1 and 300s, got {timeout}"
                )
        return v


class ObservabilitySettings(BaseSettings):
    """Settings for observability and tracing."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # LangSmith Tracing
    langchain_tracing_v2: bool = False
    langchain_endpoint: str = "https://api.smith.langchain.com"
    langchain_api_key: str | None = None
    langchain_project: str = "digital-courtroom"

    # Redaction
    pii_masking_enabled: bool = True

    # LangSmith Performance
    langsmith_timeout: int = 5
    langsmith_retries: int = 3


class DetectiveSettings(BaseSettings):
    """Settings for Layer 1 Detective nodes."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Global timeout for all external detective operations (FR-008)
    operation_timeout_seconds: int = 60

    # Multimodal LLM parameters (FR-011)
    llm_temperature: float = 0.0

    # Vision Config
    vision_provider: Literal["google", "ollama"] = Field(
        default="google", validation_alias="VISION_PROVIDER"
    )
    vision_model_id: str = Field(
        default="gemini-2.0-flash", validation_alias="VISION_MODEL"
    )

    @property
    def vision_model(self) -> str:
        """Pull from hardened_config or fallback to default."""
        return hardened_config.models.get("vision", self.vision_model_id)


class JudicialSettings(BaseSettings):
    """Settings for Layer 2 Judicial nodes."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Judicial LLM parameters
    llm_temperature: float = 0.0
    gemini_api_key: str | None = None
    google_api_key: str | None = None

    # Model Selection (picked up from ENV such as PROSECUTOR_MODEL)
    prosecutor_model_id: str = Field(
        default="deepseek-v3.1:671b-cloud", validation_alias="PROSECUTOR_MODEL"
    )
    defense_model_id: str = Field(
        default="deepseek-v3.1:671b-cloud", validation_alias="DEFENSE_MODEL"
    )
    techlead_model_id: str = Field(
        default="deepseek-v3.1:671b-cloud", validation_alias="TECHLEAD_MODEL"
    )

    @property
    def prosecutor_model(self) -> str:
        return hardened_config.models.get("prosecutor", self.prosecutor_model_id)

    @property
    def defense_model(self) -> str:
        return hardened_config.models.get("defense", self.defense_model_id)

    @property
    def techlead_model(self) -> str:
        return hardened_config.models.get("techlead", self.techlead_model_id)

    # --- Bounded Concurrency Settings (012-bounded-agent-eval) ---
    root_node: str | None = None

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

    # (013-ironclad-hardening) Redundancy and Leader Election
    judicial_redundancy_factor: int = Field(
        default=1, ge=1, le=5, validation_alias="JUDICIAL_REDUNDANCY_FACTOR"
    )

    @field_validator("max_concurrent_llm_calls")
    @classmethod
    def validate_concurrency_limit(cls, v: int) -> int:
        """FR-001: Reject invalid concurrency limits at startup."""
        if v < 1:
            raise ValueError(
                f"MAX_CONCURRENT_LLM_CALLS must be >= 1, got {v}",
            )
        if v > 50:
            raise ValueError(
                f"MAX_CONCURRENT_LLM_CALLS must be <= 50, got {v}",
            )
        return v


settings = ObservabilitySettings()
detective_settings = DetectiveSettings()
judicial_settings = JudicialSettings()
hardened_config = HardenedConfig()
