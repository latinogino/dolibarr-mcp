"""Utility helpers shared by command line entry points."""

from __future__ import annotations

import asyncio
import sys
from typing import Optional

from .config import Config
from .dolibarr_client import DolibarrClient


async def _run_test(url: Optional[str], api_key: Optional[str]) -> int:
    """Execute the Dolibarr connectivity test returning an exit code."""

    try:
        config = Config()
        if url:
            config.dolibarr_url = url
        if api_key:
            config.api_key = api_key
    except Exception as exc:  # pragma: no cover - defensive printing
        print(f"❌ Configuration error: {exc}", file=sys.stderr)
        return 1

    try:
        async with DolibarrClient(config) as client:
            print("🧪 Testing Dolibarr API connection...")
            result = await client.get_status()

            if "success" in result or "dolibarr_version" in str(result):
                print("✅ Connection successful!")
                if isinstance(result, dict) and "success" in result:
                    version = result.get("success", {}).get("dolibarr_version", "Unknown")
                    print(f"Dolibarr Version: {version}")
                return 0

            print(f"⚠️ API responded unexpectedly: {result}")
            print("⚠️ Server will run but API calls may fail")
            return 2

    except Exception as exc:  # pragma: no cover - network failure path
        print(f"❌ Test failed: {exc}", file=sys.stderr)
        return 1


def test_connection(url: Optional[str] = None, api_key: Optional[str] = None) -> int:
    """Synchronously test the Dolibarr API connection.

    Parameters mirror the CLI flags and environment variables.
    Returns an exit code compatible with `sys.exit`.
    """

    return asyncio.run(_run_test(url=url, api_key=api_key))

