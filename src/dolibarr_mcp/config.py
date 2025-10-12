"""Configuration management for Dolibarr MCP Server."""

import os
import sys

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config(BaseSettings):
    """Configuration for Dolibarr MCP Server."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_assignment=True,
        extra="forbid",
    )

    dolibarr_url: str = Field(
        description="Dolibarr API URL",
        default="",
    )

    dolibarr_api_key: str = Field(
        description="Dolibarr API key",
        default="",
        validation_alias=AliasChoices("dolibarr_api_key", "api_key"),
    )

    log_level: str = Field(
        description="Logging level",
        default="INFO",
    )

    @field_validator("dolibarr_url")
    @classmethod
    def validate_dolibarr_url(cls, v: str) -> str:
        """Validate Dolibarr URL."""
        if not v:
            v = os.getenv("DOLIBARR_URL") or os.getenv("DOLIBARR_BASE_URL", "")
            if not v:
                # Print warning but don't fail
                print(
                    "⚠️ DOLIBARR_URL/DOLIBARR_BASE_URL not configured - API calls will fail",
                    file=sys.stderr,
                )
                return "https://your-dolibarr-instance.com/api/index.php"

        if not v.startswith(("http://", "https://")):
            raise ValueError("DOLIBARR_URL must start with http:// or https://")

        # Remove trailing slash if present
        v = v.rstrip("/")

        # Ensure it ends with the proper API path
        if not v.endswith("/api/index.php"):
            if "/api" in v:
                if not v.endswith("/index.php"):
                    if v.endswith("/index.php/"):
                        v = v[:-1]
                    elif not v.endswith("/index.php"):
                        v = v + "/index.php"
            else:
                v = v + "/api/index.php"

        return v

    @field_validator("dolibarr_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key."""
        if not v:
            v = os.getenv("DOLIBARR_API_KEY", "")
            if not v:
                print(
                    "⚠️ DOLIBARR_API_KEY not configured - API authentication will fail",
                    file=sys.stderr,
                )
                print(
                    "📝 Please set DOLIBARR_API_KEY in your .env file or Claude configuration",
                    file=sys.stderr,
                )
                return "placeholder_api_key"

        if v == "your_dolibarr_api_key_here":
            print(
                "⚠️ Using placeholder API key - please configure a real API key",
                file=sys.stderr,
            )

        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        if not v:
            v = os.getenv("LOG_LEVEL", "INFO")

        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            print(f"⚠️ Invalid LOG_LEVEL '{v}', using INFO", file=sys.stderr)
            return "INFO"
        return v.upper()

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables with validation."""
        try:
            config = cls(
                dolibarr_url=os.getenv("DOLIBARR_URL") or os.getenv("DOLIBARR_BASE_URL", ""),
                dolibarr_api_key=os.getenv("DOLIBARR_API_KEY", ""),
                log_level=os.getenv("LOG_LEVEL", "INFO"),
            )
            if os.getenv("DEBUG_CONFIG"):
                print(f"✅ Config loaded:", file=sys.stderr)
                print(f"   URL: {config.dolibarr_url}", file=sys.stderr)
                print(
                    f"   API Key: {'*' * 10 if config.dolibarr_api_key else 'NOT SET'}",
                    file=sys.stderr,
                )
            return config
        except Exception as e:
            print(f"❌ Configuration Error: {e}", file=sys.stderr)
            print(file=sys.stderr)
            print("💡 Quick Setup Guide:", file=sys.stderr)
            print("1. Copy .env.example to .env", file=sys.stderr)
            print("2. Edit .env with your Dolibarr details:", file=sys.stderr)
            print(
                "   DOLIBARR_URL=https://your-dolibarr-instance.com",
                file=sys.stderr,
            )
            print(
                "   (or DOLIBARR_BASE_URL=https://your-dolibarr-instance.com/api/index.php/)",
                file=sys.stderr,
            )
            print("   DOLIBARR_API_KEY=your_api_key_here", file=sys.stderr)
            print(file=sys.stderr)
            print("🔧 Dolibarr API Key Setup:", file=sys.stderr)
            print("   1. Login to Dolibarr as admin", file=sys.stderr)
            print("   2. Go to: Home → Setup → Modules", file=sys.stderr)
            print("   3. Enable: 'Web Services API REST (developer)'", file=sys.stderr)
            print("   4. Go to: Home → Setup → API/Web services", file=sys.stderr)
            print("   5. Create a new API key", file=sys.stderr)
            print(file=sys.stderr)
            raise

    def validate_config(self) -> None:
        """Validate current configuration values."""
        self.dolibarr_url = type(self).validate_dolibarr_url(self.dolibarr_url)
        self.dolibarr_api_key = type(self).validate_api_key(self.dolibarr_api_key)
        self.log_level = type(self).validate_log_level(self.log_level)

        if self.dolibarr_url.endswith('your-dolibarr-instance.com/api/index.php') or self.dolibarr_api_key in {'', 'placeholder_api_key', 'your_dolibarr_api_key_here'}:
            raise ValueError('Dolibarr configuration is incomplete')

    @property
    def api_key(self) -> str:
        """Backward compatibility for api_key property."""
        return self.dolibarr_api_key

    @api_key.setter
    def api_key(self, value: str) -> None:
        """Allow updating the API key via legacy attribute."""
        self.dolibarr_api_key = value
