"""Tests for MCP server connection checks."""

import pytest

from dolibarr_mcp import dolibarr_mcp_server
from dolibarr_mcp.config import Config
from dolibarr_mcp.dolibarr_client import DolibarrAPIError


class _DummyClient:
    """Simple dummy client for test_api_connection success path."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    async def get_status(self):
        return {"success": {"dolibarr_version": "1.0.0"}}


class _ErrorClient:
    """Dummy client that raises for test_api_connection error path."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    async def get_status(self):
        raise DolibarrAPIError("boom")


@pytest.mark.asyncio
async def test_api_connection_success(monkeypatch):
    """Yields True when the Dolibarr API status call succeeds."""
    monkeypatch.setattr(dolibarr_mcp_server, "DolibarrClient", lambda config: _DummyClient())
    config = Config(
        dolibarr_url="https://example.com/api/index.php",
        dolibarr_api_key="test_key",
    )

    async with dolibarr_mcp_server.test_api_connection(config) as api_ok:
        assert api_ok is True


@pytest.mark.asyncio
async def test_api_connection_missing_configuration():
    """Yields False when the configuration is incomplete."""
    config = Config(
        dolibarr_url="https://your-dolibarr-instance.com/api/index.php",
        dolibarr_api_key="placeholder_api_key",
    )

    async with dolibarr_mcp_server.test_api_connection(config) as api_ok:
        assert api_ok is False


@pytest.mark.asyncio
async def test_api_connection_with_client_error(monkeypatch):
    """Yields False when the Dolibarr client raises errors."""
    monkeypatch.setattr(dolibarr_mcp_server, "DolibarrClient", lambda config: _ErrorClient())
    config = Config(
        dolibarr_url="https://example.com/api/index.php",
        dolibarr_api_key="test_key",
    )

    async with dolibarr_mcp_server.test_api_connection(config) as api_ok:
        assert api_ok is False
