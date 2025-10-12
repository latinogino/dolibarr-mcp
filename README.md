# Dolibarr MCP Server

A focused Model Context Protocol (MCP) server for managing a Dolibarr ERP/CRM
instance. The codebase mirrors the clean, minimal structure of
[`prestashop-mcp`](https://github.com/latinogino/prestashop-mcp): a single MCP
entry point, a compact async client and thorough documentation that lives in the
`docs/` directory.

## Repository layout

| Path | Purpose |
| --- | --- |
| `src/dolibarr_mcp/` | MCP server implementation, configuration helpers and CLI utilities |
| `tests/` | Automated pytest suite covering configuration, client behaviour and tool registration |
| `docs/` | Developer and operator documentation (quickstart, configuration, API coverage) |
| `docker/` | Optional container assets for local stacks and deployments |

## Quickstart

Follow the platform specific guides in [`docs/quickstart.md`](docs/quickstart.md)
for detailed steps. The short version:

```bash
git clone https://github.com/latinogino/dolibarr-mcp.git
cd dolibarr-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

On Windows launch a Visual Studio developer shell (`vsenv`), create the virtual
environment with `py -3 -m venv .venv` and activate it via
`.\.venv\Scripts\Activate.ps1` before running `pip install -e .`.

Install developer tooling when you need the test-suite:

```bash
pip install -e '.[dev]'
```

PowerShell requires escaping the brackets: `pip install -e .`[dev`]`.

## Configuration

Define the following environment variables (or place them in a `.env` file):

- `DOLIBARR_URL` – API entry point, e.g. `https://your-dolibarr.example.com/api/index.php`
- `DOLIBARR_API_KEY` – personal API token
- `LOG_LEVEL` – optional logging verbosity

The [`Config` helper](src/dolibarr_mcp/config.py) validates and normalises these
values using `pydantic-settings`. See [`docs/configuration.md`](docs/configuration.md)
for more context.

## Running the server

The server communicates over STDIO as required by MCP. Start it with:

```bash
python -m dolibarr_mcp.cli serve
```

Use the CLI to confirm your credentials before connecting through an MCP host:

```bash
python -m dolibarr_mcp.cli test --url https://your-dolibarr.example.com/api/index.php --api-key YOUR_KEY
```

## Available tools

`dolibarr_mcp_server` registers a collection of MCP tools that cover common ERP
workflows:

- **System** – `test_connection`, `get_status`
- **Users** – `get_users`, `get_user_by_id`, `create_user`, `update_user`, `delete_user`
- **Customers / Third parties** – `get_customers`, `get_customer_by_id`, `create_customer`, `update_customer`, `delete_customer`
- **Products** – `get_products`, `get_product_by_id`, `create_product`, `update_product`, `delete_product`
- **Invoices** – `get_invoices`, `get_invoice_by_id`, `create_invoice`, `update_invoice`, `delete_invoice`
- **Orders** – `get_orders`, `get_order_by_id`, `create_order`, `update_order`, `delete_order`
- **Contacts** – `get_contacts`, `get_contact_by_id`, `create_contact`, `update_contact`, `delete_contact`
- **Raw API access** – `dolibarr_raw_api`

The async implementation in [`dolibarr_client.py`](src/dolibarr_mcp/dolibarr_client.py)
provides the underlying HTTP operations, error handling and pagination helpers
used by these tools. A concise REST coverage overview is available in
[`docs/api-reference.md`](docs/api-reference.md).

## Development

- Run the automated test-suite with `pytest`. Coverage options and Docker
  helpers are documented in [`docs/development.md`](docs/development.md).
- The project is packaged with `pyproject.toml`; editable installs use the `src/`
  layout and register the `dolibarr-mcp` console entry point.

## License

This project is released under the [MIT License](LICENSE).
