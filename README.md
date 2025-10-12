# Dolibarr MCP Server

A focused Model Context Protocol (MCP) server for managing a Dolibarr ERP/CRM instance.  
The MCP entry point lives in [`src/dolibarr_mcp/dolibarr_mcp_server.py`](src/dolibarr_mcp/dolibarr_mcp_server.py) and exposes
Dolibarr management tools to MCP compatible clients such as Claude Desktop.

## Repository layout

| Path | Purpose |
| --- | --- |
| `src/dolibarr_mcp/` | MCP server, configuration helpers and CLI utilities |
| `tests/` | Automated pytest suite covering configuration and client logic |
| `api/` | Notes collected while analysing the Dolibarr REST API |

Everything else in the repository supports one of these three areas.

## Installation

### Linux / macOS

```bash
# Clone the repository
git clone https://github.com/latinogino/dolibarr-mcp.git
cd dolibarr-mcp

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the package in editable mode together with runtime dependencies
pip install -e .
```

### Windows (PowerShell)

```powershell
# Launch a Visual Studio developer shell so native extensions such as aiohttp can build
vsenv

# Clone the repository
git clone https://github.com/latinogino/dolibarr-mcp.git
Set-Location dolibarr-mcp

# Create and activate a virtual environment
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install the package in editable mode together with runtime dependencies
pip install -e .
```

> 💡 If you do not already have the Visual Studio developer PowerShell available, open the
> **"Developer PowerShell for VS"** shortcut first. Inside that shell the `vsenv` command
> initialises the Visual Studio build environment that `pip` needs to compile `aiohttp` and
> other native wheels on Windows.

For contributors who need the development tooling (pytest, coverage, etc.) install the optional
extras:

```bash
# Linux / macOS
pip install -e '.[dev]'
```

```powershell
# Windows PowerShell
pip install -e .`[dev`]
```

## Configuration

Create a `.env` file (or set the variables in your MCP host application) with:

```env
DOLIBARR_URL=https://your-dolibarr.example.com/api/index.php
DOLIBARR_API_KEY=your_api_key
LOG_LEVEL=INFO
```

The [`Config` helper](src/dolibarr_mcp/config.py) loads these values, validates them and provides sensible
warnings when something is missing.

## Running the server

The server communicates over STDIO as required by MCP. Start it with one of the following commands:

```bash
# Use the Python module entry point
python -m dolibarr_mcp

# Or use the CLI wrapper installed by the package
python -m dolibarr_mcp.cli serve
# Alias when installed as a package: dolibarr-mcp serve
```

To check that Dolibarr credentials are working you can run:

```bash
python -m dolibarr_mcp.cli test --url https://your-dolibarr.example.com/api/index.php --api-key YOUR_KEY
```

## Available tools

`dolibarr_mcp_server` registers a collection of MCP tools that cover common ERP workflows:

- **System** – `test_connection`, `get_status`
- **Users** – `get_users`, `get_user_by_id`, `create_user`, `update_user`, `delete_user`
- **Customers / Third parties** – `get_customers`, `get_customer_by_id`, `create_customer`, `update_customer`, `delete_customer`
- **Products** – `get_products`, `get_product_by_id`, `create_product`, `update_product`, `delete_product`
- **Invoices** – `get_invoices`, `get_invoice_by_id`, `create_invoice`, `update_invoice`, `delete_invoice`
- **Orders** – `get_orders`, `get_order_by_id`, `create_order`, `update_order`, `delete_order`
- **Contacts** – `get_contacts`, `get_contact_by_id`, `create_contact`, `update_contact`, `delete_contact`
- **Raw API access** – `dolibarr_raw_api`

The implementation in [`dolibarr_client.py`](src/dolibarr_mcp/dolibarr_client.py) provides the underlying async HTTP
operations, error handling and pagination helpers used by these tools.

## Development

- Run the automated test-suite with `pytest`.
- The project is packaged with `pyproject.toml`; editable installs use the `src/` layout.
- Additional API notes live in the [`api/`](api) directory if you need to extend the toolset.

## License

This project is released under the [MIT License](LICENSE).
