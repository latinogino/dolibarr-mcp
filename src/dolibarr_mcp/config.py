"""Configuration management for Dolibarr MCP Server."""

import os
import sys
from typing import Optional

from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config(BaseModel):
    """Configuration for Dolibarr MCP Server."""
    
    dolibarr_url: str = Field(
        description="Dolibarr API URL",
        default_factory=lambda: os.getenv("DOLIBARR_URL") or os.getenv("DOLIBARR_BASE_URL", "")
    )
    
    api_key: str = Field(
        description="Dolibarr API key",
        default_factory=lambda: os.getenv("DOLIBARR_API_KEY", "")
    )
    
    log_level: str = Field(
        description="Logging level",
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )
    
    @validator('dolibarr_url')
    def validate_dolibarr_url(cls, v):
        """Validate Dolibarr URL."""
        if not v:
            # Print warning but don't fail
            print("⚠️ DOLIBARR_URL/DOLIBARR_BASE_URL not configured - API calls will fail", file=sys.stderr)
            return "https://your-dolibarr-instance.com/api/index.php"
        
        if not v.startswith(('http://', 'https://')):
            raise ValueError("DOLIBARR_URL must start with http:// or https://")
        
        # Remove trailing slash if present
        v = v.rstrip('/')
        
        # Ensure it ends with the proper API path
        if not v.endswith('/api/index.php'):
            # Check if it already has /api somewhere
            if '/api' in v:
                # Just ensure it ends properly
                if not v.endswith('/index.php'):
                    # Check if it ends with /api/index.php/
                    if v.endswith('/index.php/'):
                        v = v[:-1]  # Remove trailing slash
                    elif not v.endswith('/index.php'):
                        v = v + '/index.php'
            else:
                # Add the full API path
                v = v + '/api/index.php'
                
        return v
    
    @validator('api_key')
    def validate_api_key(cls, v):
        """Validate API key."""
        if not v:
            # Print warning but don't fail
            print("⚠️ DOLIBARR_API_KEY not configured - API authentication will fail", file=sys.stderr)
            print("📝 Please set DOLIBARR_API_KEY in your .env file or Claude configuration", file=sys.stderr)
            return "placeholder_api_key"
        
        if v == "your_dolibarr_api_key_here":
            print("⚠️ Using placeholder API key - please configure a real API key", file=sys.stderr)
            
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {', '.join(valid_levels)}")
        return v.upper()
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables with validation."""
        try:
            config = cls()
            # Debug output for troubleshooting
            if os.getenv("DEBUG_CONFIG"):
                print(f"✅ Config loaded:", file=sys.stderr)
                print(f"   URL: {config.dolibarr_url}", file=sys.stderr)
                print(f"   API Key: {'*' * 10 if config.api_key else 'NOT SET'}", file=sys.stderr)
            return config
        except Exception as e:
            print(f"❌ Configuration Error: {e}", file=sys.stderr)
            print(file=sys.stderr)
            print("💡 Quick Setup Guide:", file=sys.stderr)
            print("1. Copy .env.example to .env", file=sys.stderr)
            print("2. Edit .env with your Dolibarr details:", file=sys.stderr)
            print("   DOLIBARR_URL=https://your-dolibarr-instance.com", file=sys.stderr)
            print("   (or DOLIBARR_BASE_URL=https://your-dolibarr-instance.com/api/index.php/)", file=sys.stderr)
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
    
    class Settings:
        """Pydantic settings configuration."""
        env_file = '.env'
        env_file_encoding = 'utf-8'
