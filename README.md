# Dolibarr MCP Server

Dolibarr MCP is a focused Model Context Protocol (MCP) server that exposes the
most useful Dolibarr ERP/CRM operations to AI copilots. The repository mirrors
the clean layout used by [`prestashop-mcp`](https://github.com/latinogino/prestashop-mcp):
a single production-ready server implementation, an async HTTP client, and a
self-contained documentation bundle.

| Path | Purpose |
| --- | --- |

This MCP server enables complete management of your Dolibarr ERP/CRM through AI
tools such as Claude Desktop. With specialised tools you can manage customers,
products, invoices, orders, contacts, and system administration tasks from a
single MCP endpoint.

## 📚 Documentation

All user and contributor guides live in [`docs/`](docs/README.md):

- [Quickstart](docs/quickstart.md) – installation and first run instructions for Linux, macOS, and Windows
- [Configuration](docs/configuration.md) – environment variables and secrets consumed by the server
- [Development](docs/development.md) – test workflow, linting, and Docker helpers
- [API Reference](docs/api-reference.md) – Dolibarr REST resources and corresponding MCP tools

## ✨ Features

- **💼 Complete ERP/CRM Management** – Tools for customers, products, invoices, orders, and contacts
- **⚡ Async/Await Architecture** – Modern, high-performance HTTP client and server
- **🛡️ Comprehensive Error Handling** – Robust validation and structured responses
- **🐳 Docker Support** – Optional container workflow for local experimentation and deployment
- **🔧 Production-Ready** – Automated tests and configuration management powered by `pydantic-settings`

## 🛠 Available tools

`dolibarr_mcp_server` registers MCP tools that map to common Dolibarr workflows.
See the [API reference](docs/api-reference.md) for full details.

- **System** – `test_connection`, `get_status`, and `dolibarr_raw_api`
- **Users** – CRUD helpers for Dolibarr users
- **Customers / Third Parties** – CRUD helpers for partners
- **Products** – CRUD helpers for product catalogue entries
- **Invoices** – CRUD helpers for invoices
- **Orders** – CRUD helpers for customer orders
- **Contacts** – CRUD helpers for contact records

The async implementation in [`dolibarr_client.py`](src/dolibarr_mcp/dolibarr_client.py)
handles authentication, pagination, and error handling for all endpoints.

## 📦 Installation

### Linux / macOS

```bash
git clone https://github.com/latinogino/dolibarr-mcp.git
cd dolibarr-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Install development extras (pytest, formatting, type-checking) when needed:

```bash
pip install -e '.[dev]'
```

### Windows (Visual Studio `vsenv`)

1. Launch the **x64 Native Tools Command Prompt for VS** or **Developer PowerShell for VS** (`vsenv`).
2. Create a virtual environment: `py -3 -m venv .venv`.
3. Activate it: `call .venv\\Scripts\\activate.bat` (Command Prompt) or `.\\.venv\\Scripts\\Activate.ps1` (PowerShell).
4. Install the package: `pip install -e .`.
5. Install development extras when required: `pip install -e .[dev]` (PowerShell requires escaping brackets: ``pip install -e .`[dev`]``).
6. Note the Python path (`where python`) for integration with Claude Desktop or other MCP hosts.

### Docker

```bash
# Using Docker Compose (recommended)
docker compose up -d

# Or build and run directly
docker build -t dolibarr-mcp .
docker run -d \
  -e DOLIBARR_URL=https://your-dolibarr.example.com/api/index.php \
  -e DOLIBARR_API_KEY=YOUR_API_KEY \
  dolibarr-mcp
```

## ⚙️ Configuration

Set the following environment variables (they may live in a `.env` file):

- `DOLIBARR_URL` – Dolibarr API endpoint, e.g. `https://example.com/api/index.php`
- `DOLIBARR_API_KEY` – personal Dolibarr API token
- `LOG_LEVEL` – optional logging verbosity (defaults to `INFO`)

[`Config`](src/dolibarr_mcp/config.py) is built with `pydantic-settings` and
supports loading from the environment, `.env` files, and CLI overrides. See the
[configuration guide](docs/configuration.md) for a full matrix and troubleshooting tips.

## ▶️ Running the server

Dolibarr MCP communicates with hosts over STDIO. Once configured, launch the
server with:

```bash
python -m dolibarr_mcp.cli serve
```

You can validate credentials and connectivity using the built-in test command
before wiring it into a host:

```bash
python -m dolibarr_mcp.cli test --url https://example.com/api/index.php --api-key YOUR_TOKEN
```

## 🤖 Using with Claude Desktop

Add an entry to `claude_desktop_config.json` that points to your virtual
environment’s Python executable and the `dolibarr_mcp.cli` module. After
installation, verify the executable path with `which python` (Linux/macOS) or
`where python` (Windows `vsenv`). Restart Claude Desktop so it picks up the new
MCP server.

## 🧪 Development workflow

- Run the test-suite with `pytest` (see [development docs](docs/development.md)
  for coverage flags and Docker helpers).
- Editable installs rely on the `src/` layout and expose the `dolibarr-mcp`
  console entry point.
- Contributions follow the same structure and documentation conventions as
  `prestashop-mcp` to keep the twin projects in sync.

## 📄 License
=======
```bash
python -m dolibarr_mcp.cli test --url https://your-dolibarr.example.com/api/index.php --api-key YOUR_KEY
```

## Available tools

- **System** – `test_connection`, `get_status`
- **Users** – `get_users`, `get_user_by_id`, `create_user`, `update_user`, `delete_user`
- **Customers / Third parties** – `get_customers`, `get_customer_by_id`, `create_customer`, `update_customer`, `delete_customer`
- **Products** – `get_products`, `get_product_by_id`, `create_product`, `update_product`, `delete_product`
- **Invoices** – `get_invoices`, `get_invoice_by_id`, `create_invoice`, `update_invoice`, `delete_invoice`
- **Orders** – `get_orders`, `get_order_by_id`, `create_order`, `update_order`, `delete_order`
- **Contacts** – `get_contacts`, `get_contact_by_id`, `create_contact`, `update_contact`, `delete_contact`
- **Raw API access** – `dolibarr_raw_api`


## License

This project is released under the [MIT License](LICENSE).
