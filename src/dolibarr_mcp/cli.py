"""Command line interface for Dolibarr MCP Server."""

import asyncio
import sys
from typing import Optional

import click

from .dolibarr_mcp_server import main as server_main
from .testing import test_connection as run_test_connection


@click.group()
@click.version_option(version="1.1.0", prog_name="dolibarr-mcp")
def cli():
    """Dolibarr MCP Server - Professional ERP integration via Model Context Protocol."""
    pass


@cli.command()
@click.option("--url", help="Dolibarr API URL")
@click.option("--api-key", help="Dolibarr API key")
def test(url: Optional[str], api_key: Optional[str]):
    """Test the connection to Dolibarr API."""
    exit_code = run_test_connection(url=url, api_key=api_key)
    if exit_code != 0:
        sys.exit(exit_code)


@cli.command()
@click.option("--host", default="localhost", help="Host to bind to")
@click.option("--port", default=8080, help="Port to bind to") 
def serve(host: str, port: int):
    """Start the Dolibarr MCP server."""
    click.echo(f"🚀 Starting Dolibarr MCP server on {host}:{port}")
    click.echo("📝 Use this server with MCP-compatible clients")
    click.echo("🔧 Configure your environment variables in .env file")
    
    # Run the MCP server
    asyncio.run(server_main())


@cli.command()
def version():
    """Show version information."""
    click.echo("Dolibarr MCP Server v1.1.0")
    click.echo("Professional ERP integration via Model Context Protocol")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
