# Dolibarr MCP Server

Dolibarr MCP delivers a Model Context Protocol (MCP) interface for the Dolibarr
ERP/CRM. The project mirrors the project structure of [`prestashop-mcp`](https://github.com/latinogino/prestashop-mcp):
an async API client, a production-ready STDIO server, and focused
documentation.

**Design Note:** While sharing the same architecture, this server implements **specialized search tools** (e.g., `search_products_by_ref`, `resolve_product_ref`) instead of a single unified `get_` tool. This design choice ensures efficient server-side filtering via Dolibarr's SQL API, preventing the agent from accidentally loading thousands of records and exceeding context limits.

Claude Desktop and other MCP-aware tools can use the server to
manage customers, products, invoices, orders, and contacts in a Dolibarr
instance.

Consult the bundled [documentation index](docs/README.md) for deep dives into
configuration, API coverage, and contributor workflows.

## ✨ Features

- **Full ERP coverage** – CRUD tools for users, customers, products, invoices,
  orders, contacts, projects, and raw API access.
- **Advanced Search** – Server-side filtering for products, customers, and projects to minimize token usage and costs.
- **Async/await HTTP client** – Efficient Dolibarr API wrapper with structured
  error handling.
- **Ready for MCP hosts** – STDIO transport compatible with Claude Desktop out
  of the box.
- **Shared workflow with prestashop-mcp** – Identical developer ergonomics and
  documentation structure across both repositories.

## ✅ Prerequisites

- Python 3.8 or newer.
- Access to a Dolibarr installation with the REST API enabled and a personal API
  token.

## 📦 Installation

### Linux / macOS

```bash
git clone https://github.com/latinogino/dolibarr-mcp.git
cd dolibarr-mcp
python3 -m venv venv_dolibarr
source venv_dolibarr/bin/activate
pip install -e .
# Optional development extras
pip install -e '.[dev]'
```

While the virtual environment is active record the Python executable path with
`which python`. Claude Desktop must launch the MCP server using this interpreter.

### Windows (PowerShell)

```powershell
git clone https://github.com/latinogino/dolibarr-mcp.git
Set-Location dolibarr-mcp
py -3 -m venv venv_dolibarr
./venv_dolibarr/Scripts/Activate.ps1
pip install -e .
# Optional development extras (escape brackets in PowerShell)
pip install -e .`[dev`]
```

Run `Get-Command python` (or `Get-Command python.exe`) while the environment is
activated and note the absolute path. Claude Desktop should use this interpreter
inside the virtual environment, for example
`C:\\path\\to\\dolibarr-mcp\\venv_dolibarr\\Scripts\\python.exe`.

### Docker (optional)

```bash
# Copy the template and update credentials (file is gitignored)
cp .env.example .env

# Start the HTTP listener for MCP clients (Open WebUI, MCPO, etc.)
docker compose up -d
# or
docker build -t dolibarr-mcp .
docker run -d \
  -e DOLIBARR_URL=https://your-dolibarr.example.com/api/index.php \
  -e DOLIBARR_API_KEY=YOUR_API_KEY \
  dolibarr-mcp
```

## ⚙️ Configuration

### Environment variables

The server reads configuration from the environment or a `.env` file. Both
`DOLIBARR_URL` and `DOLIBARR_SHOP_URL` are accepted for the base API address.
The repository `.gitignore` excludes `.env`, so a local `.env` file will not be
overwritten by `git pull` on your server.

| Variable | Description |
| --- | --- |
| `DOLIBARR_URL` / `DOLIBARR_SHOP_URL` | Base Dolibarr API endpoint, e.g. `https://example.com/api/index.php`. Trailing slashes are handled automatically. |
| `DOLIBARR_API_KEY` | Personal Dolibarr API token. |
| `LOG_LEVEL` | Optional logging verbosity (`INFO`, `DEBUG`, `WARNING`, …). |
| `MCP_TRANSPORT` | Transport to use: `stdio` (default) or `http` for streamable HTTP. |
| `MCP_HTTP_HOST` | Host/interface to bind when using HTTP transport (default `127.0.0.1`). |
| `MCP_HTTP_TOKEN` | Bearer token required on every HTTP request. **Mandatory** when `MCP_HTTP_HOST` is not a loopback address (always the case in Docker). |
| `MCP_CORS_ORIGINS` | Comma-separated list of allowed browser origins. Empty (default) disables CORS. |
| `MCP_READ_ONLY` | `true` exposes only read tools (no create/update/delete/validate). Default `false`. |
| `MCP_ENABLE_RAW_API` | `true` exposes the `dolibarr_raw_api` tool (arbitrary API calls). Default `false`. |
| `MCP_BIND_ADDRESS` | Host interface published by Docker Compose (default `127.0.0.1`). |
| `MCP_HTTP_PORT` | Port to bind when using HTTP transport (default `8080`). |
| `MCP_HOST_PORT` | Optional host port to publish in Docker Compose (default `18004`). |
| `MCP_CONTAINER_NAME` | Optional Docker Compose container name (default `dolibarr-mcp-server`). |
| `MCP_NETWORK_NAME` | Optional Docker Compose network name (default `dolibarr-mcp-net`). |
| `MCP_NETWORK_EXTERNAL` | Set to `true` to reuse an existing Docker network (default `false`). |

Example `.env`:

```env
DOLIBARR_URL=https://your-dolibarr.example.com/api/index.php
DOLIBARR_API_KEY=YOUR_API_KEY
LOG_LEVEL=INFO
MCP_CONTAINER_NAME=dolibarr-mcp-server
MCP_NETWORK_NAME=dolibarr-mcp-net
MCP_NETWORK_EXTERNAL=false
```

### Claude Desktop configuration

Add the following block to `claude_desktop_config.json`, replacing the paths and
credentials with your own values:

```json
{
  "mcpServers": {
    "dolibarr": {
      "command": "C:\\path\\to\\dolibarr-mcp\\venv_dolibarr\\Scripts\\python.exe",
      "args": ["-m", "dolibarr_mcp.dolibarr_mcp_server"],
      "cwd": "C:\\path\\to\\dolibarr-mcp",
      "env": {
        "DOLIBARR_SHOP_URL": "https://your-dolibarr.example.com",
        "DOLIBARR_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

Restart Claude Desktop after saving the configuration. The MCP server reads the
same environment variables when launched from Linux or macOS hosts.

### Open WebUI configuration

Open WebUI connects to the Dolibarr MCP server over Streamable HTTP, so start
the server with `MCP_TRANSPORT=http` (locally or via Docker Compose) and then
add a new MCP server in **Settings → Admin → MCP Servers**.

Example configuration (URL + optional headers):

```json
{
  "name": "dolibarr",
  "url": "http://localhost:8080/",
  "headers": {
    "mcp-protocol-version": "2024-11-05",
    "Authorization": "Bearer <MCP_HTTP_TOKEN>"
  }
}
```

If you are running Docker Compose, point the URL at
`http://<host>:${MCP_HOST_PORT:-18004}/` instead.

### LM Studio configuration

LM Studio also connects over Streamable HTTP. Ensure the server is running with
`MCP_TRANSPORT=http` and then open **Settings → MCP Servers → Add Server**.

Example entry:

```text
Name: dolibarr
URL:  http://localhost:8080/
Header: Authorization: Bearer <MCP_HTTP_TOKEN>
```

If you are using Docker, substitute the host port published by
`docker-compose.yml`, for example `http://localhost:18004/`.

### 🔒 Security

- **HTTP authentication**: set `MCP_HTTP_TOKEN` (e.g. `openssl rand -hex 32`); clients must
  send `Authorization: Bearer <token>`. The server refuses to listen on a non-loopback
  interface without a token, and Docker Compose refuses to start without it.
- **Network exposure**: the listener binds `127.0.0.1` by default and Docker Compose
  publishes the port on `127.0.0.1` only. Expose it further only behind a VPN or an
  authenticated reverse proxy (`MCP_BIND_ADDRESS`).
- **CORS** is disabled unless origins are listed in `MCP_CORS_ORIGINS`.
- **Least privilege**: create a dedicated Dolibarr user with minimal rights for the API key,
  use `MCP_READ_ONLY=true` when write access is not needed, and keep
  `dolibarr_raw_api` disabled (`MCP_ENABLE_RAW_API=false`) unless required.

## ▶️ Usage

### Start the MCP server

The server communicates over STDIO by default, so run it in the foreground from
the virtual environment:

```bash
python -m dolibarr_mcp.dolibarr_mcp_server
```

Logs are written to stderr to avoid interfering with the MCP protocol. Keep the
process running while Claude Desktop is active.

### HTTP streaming mode (for Open WebUI or remote MCP clients)

Enable the HTTP transport by setting `MCP_TRANSPORT=http` (and optionally
`MCP_HTTP_HOST` / `MCP_HTTP_PORT`). This keeps the server running without STDIO
and exposes the Streamable HTTP transport compatible with Open WebUI:

```bash
MCP_TRANSPORT=http MCP_HTTP_PORT=8080 python -m dolibarr_mcp.dolibarr_mcp_server
```

Then point Open WebUI’s MCP configuration at `http://<host>:8080/`. The MCP
protocol headers (including `mcp-protocol-version`) are handled automatically by
Open WebUI’s MCP client.

### Docker Compose listener (recommended for MCP clients)

The bundled `docker-compose.yml` starts the HTTP listener by default so MCP
clients such as Open WebUI or MCPO can connect to
`http://<host>:${MCP_HOST_PORT:-18004}/` right away.

### Test the Dolibarr credentials

Use the standalone connectivity check before wiring the server into an MCP host:

```bash
python -m dolibarr_mcp.test_connection --url https://your-dolibarr.example.com/api/index.php --api-key YOUR_API_KEY
```

When the environment variables are already set, omit the overrides and run
`python -m dolibarr_mcp.test_connection`.

## 🧪 Development

- Run the test-suite with `pytest` (see [`docs/development.md`](docs/development.md)
  for coverage options and Docker helpers).
- Editable installs rely on the `src/` layout and expose the `dolibarr-mcp`
  console entry point for backwards compatibility.
- The repository structure, tooling, and docs intentionally mirror
  [`prestashop-mcp`](https://github.com/latinogino/prestashop-mcp) to keep the
  companion projects aligned.

## 📄 License

Released under the [MIT License](LICENSE).
