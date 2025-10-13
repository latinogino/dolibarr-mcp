"""Standalone entry point to verify Dolibarr connectivity."""

from __future__ import annotations

import argparse

from .testing import test_connection


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test the Dolibarr MCP configuration")
    parser.add_argument("--url", help="Override the Dolibarr API URL", default=None)
    parser.add_argument("--api-key", help="Override the Dolibarr API key", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    exit_code = test_connection(url=args.url, api_key=args.api_key)
    raise SystemExit(exit_code)


if __name__ == "__main__":  # pragma: no cover - manual execution entry
    main()

