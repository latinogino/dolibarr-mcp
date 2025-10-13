# Configuration

The Dolibarr MCP server reads configuration from environment variables. Use a
`.env` file during development or configure the variables directly in the MCP
host application that will launch the server.

| Variable | Description |
| --- | --- |
| `DOLIBARR_URL` / `DOLIBARR_SHOP_URL` | Base API URL, e.g. `https://your-dolibarr.example.com/api/index.php` (legacy configs that still export `DOLIBARR_BASE_URL` are also honoured). |
| `DOLIBARR_API_KEY` | Personal Dolibarr API token assigned to your user. |
| `LOG_LEVEL` | Optional logging level (`INFO`, `DEBUG`, `WARNING`, …). |

## Example `.env`

```env
DOLIBARR_URL=https://your-dolibarr.example.com/api/index.php
DOLIBARR_API_KEY=your_api_key
LOG_LEVEL=INFO
```

The [`Config` class](../src/dolibarr_mcp/config.py) is built with
`pydantic-settings`. It validates the values on load, applies alias support for
legacy variable names and raises a descriptive error if placeholder credentials
are detected.

## Testing credentials

Use the standalone helper to verify that the credentials are accepted by
Dolibarr before wiring the server into your MCP host:

```bash
python -m dolibarr_mcp.test_connection --url https://your-dolibarr.example.com/api/index.php --api-key YOUR_KEY
```
