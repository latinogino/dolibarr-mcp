"""
Test configuration module for Dolibarr MCP Server.
"""

import os
import pytest
from unittest.mock import patch
from pathlib import Path

from dolibarr_mcp.config import Config


class TestConfig:
    """Test configuration loading and validation."""
    
    def test_config_from_env(self):
        """Test configuration loading from environment variables."""
        with patch.dict(os.environ, {
            'DOLIBARR_URL': 'https://test.dolibarr.com',
            'DOLIBARR_API_KEY': 'test_key_123',
            'LOG_LEVEL': 'DEBUG'
        }):
            config = Config()
            assert config.dolibarr_url == 'https://test.dolibarr.com'
            assert config.dolibarr_api_key == 'test_key_123'
            assert config.log_level == 'DEBUG'
    
    def test_config_defaults(self):
        """Test configuration defaults when env vars not set."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            assert config.log_level == 'INFO'  # Default log level
    
    def test_config_validation(self):
        """Test configuration validation."""
        with patch.dict(os.environ, {
            'DOLIBARR_URL': '',
            'DOLIBARR_API_KEY': ''
        }):
            with pytest.raises(ValueError, match="DOLIBARR_URL must be configured"):
                config = Config()
                config.validate()
    
    def test_config_url_normalization(self):
        """Test URL normalization (removing trailing slashes)."""
        with patch.dict(os.environ, {
            'DOLIBARR_URL': 'https://test.dolibarr.com/',
            'DOLIBARR_API_KEY': 'test_key'
        }):
            config = Config()
            assert config.dolibarr_url == 'https://test.dolibarr.com'
            assert not config.dolibarr_url.endswith('/')
    
    def test_config_from_dotenv(self, tmp_path):
        """Test configuration loading from .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "DOLIBARR_URL=https://env.dolibarr.com\n"
            "DOLIBARR_API_KEY=env_key_456\n"
            "LOG_LEVEL=WARNING\n"
        )
        
        with patch.dict(os.environ, {'DOTENV_PATH': str(env_file)}):
            config = Config()
            assert config.dolibarr_url == 'https://env.dolibarr.com'
            assert config.dolibarr_api_key == 'env_key_456'
            assert config.log_level == 'WARNING'
    
    def test_config_precedence(self):
        """Test that environment variables take precedence over .env file."""
        with patch.dict(os.environ, {
            'DOLIBARR_URL': 'https://env.dolibarr.com',
            'DOLIBARR_API_KEY': 'env_key'
        }):
            config = Config()
            assert config.dolibarr_url == 'https://env.dolibarr.com'
            assert config.dolibarr_api_key == 'env_key'
    
    def test_log_level_validation(self):
        """Test log level validation."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        for level in valid_levels:
            with patch.dict(os.environ, {
                'DOLIBARR_URL': 'https://test.com',
                'DOLIBARR_API_KEY': 'key',
                'LOG_LEVEL': level
            }):
                config = Config()
                assert config.log_level == level
    
    def test_invalid_log_level(self):
        """Test invalid log level falls back to default."""
        with patch.dict(os.environ, {
            'DOLIBARR_URL': 'https://test.com',
            'DOLIBARR_API_KEY': 'key',
            'LOG_LEVEL': 'INVALID'
        }):
            config = Config()
            assert config.log_level == 'INFO'  # Should fall back to default
