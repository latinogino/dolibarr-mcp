"""Command line interface for Dolibarr MCP Server."""

import asyncio
import sys
from typing import Optional

import click

from .config import Config
from .dolibarr_mcp_server import main as server_main


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
    
    async def run_test():
        try:
            # Import here to avoid circular imports
            from .dolibarr_client import DolibarrClient
            
            # Create config with optional overrides
            try:
                config = Config()
                if url:
                    config.dolibarr_url = url
                if api_key:
                    config.api_key = api_key
            except Exception as e:
                click.echo(f"❌ Configuration error: {e}")
                sys.exit(1)
            
            async with DolibarrClient(config) as client:
                click.echo("🧪 Testing Dolibarr API connection...")
                
                # Test basic status endpoint
                result = await client.get_status()
                
                if "success" in result or "dolibarr_version" in str(result):
                    click.echo("✅ Connection successful!")
                    if isinstance(result, dict) and "success" in result:
                        version = result.get("success", {}).get("dolibarr_version", "Unknown")
                        click.echo(f"Dolibarr Version: {version}")
                    
                    # Test a few more endpoints
                    try:
                        users = await client.get_users(limit=1)
                        click.echo(f"Users accessible: {len(users) if isinstance(users, list) else 'Error'}")
                    except Exception:
                        click.echo("Users: ⚠️  Access limited or unavailable")
                    
                    try:
                        customers = await client.get_customers(limit=1)
                        click.echo(f"Customers accessible: {len(customers) if isinstance(customers, list) else 'Error'}")
                    except Exception:
                        click.echo("Customers: ⚠️  Access limited or unavailable")
                    
                else:
                    click.echo(f"❌ Connection failed: {result}")
                    sys.exit(1)
                    
        except Exception as e:
            click.echo(f"❌ Test failed: {e}")
            sys.exit(1)
    
    asyncio.run(run_test())


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
