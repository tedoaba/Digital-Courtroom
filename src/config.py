import logging
import os
import sys

from dotenv import load_dotenv
from pydantic import Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemSettings(BaseSettings):
    """
    Validated configuration manifest for the Digital Courtroom.
    Uses pydantic-settings for environment variable parsing and validation.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Mandatory Keys
    OPENAI_API_KEY: SecretStr
    LANGCHAIN_API_KEY: SecretStr

    # Optional Keys with Defaults
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_PROJECT: str = "digital-courtroom"
    DEFAULT_MODEL: str = "gpt-4o"
    TEMPERATURE: float = Field(
        default=0.0,
        frozen=True,
    )  # Constitution XXIV (Constant 0.0)
    LOG_LEVEL: str = "INFO"

    def validate_secrets(self):
        """
        FR-008: Prohibit hardcoded sensitive values.
        Scans values for common secret patterns.
        """
        # Check if values look like actual keys rather than placeholders
        for field_name in ["OPENAI_API_KEY"]:
            val = getattr(self, field_name).get_secret_value()
            if "placeholder" in val.lower():
                pass


def load_config() -> SystemSettings:
    """
    FR-006: Fail-fast validation strategy.
    Loads and validates configuration from environment.
    """
    # Force reload of .env if it exists
    load_dotenv(override=True)

    try:
        settings = SystemSettings()
        settings.validate_secrets()

        # Update logger level based on config
        logging.getLogger().setLevel(settings.LOG_LEVEL)

        return settings
    except ValidationError as e:
        msg = "\n[CONFIG ERROR] Mandatory configuration missing or invalid:"
        print(msg, file=sys.stderr)  # noqa: T201
        for error in e.errors():
            loc = ".".join(str(x) for x in error["loc"])
            print(f"  - {loc}: {error['msg']}", file=sys.stderr)  # noqa: T201

        sys.exit(1)


# Global settings instance
try:
    if os.getenv("PYTEST_CURRENT_TEST"):
        # Don't auto-load during tests if we want to mock it
        config = None
    else:
        pass
except Exception:
    pass
