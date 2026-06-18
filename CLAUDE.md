# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Python MCP (Model Context Protocol) server exposing Dolibarr ERP/CRM REST API
operations as MCP tools. Request flow: **MCP tool call → `dolibarr_mcp_server.py`
dispatch → `DolibarrClient` method → Dolibarr REST API (`/api/index.php`)**.

A sibling project, [`prestashop-mcp`](https://github.com/latinogino/prestashop-mcp),
intentionally shares this repo's structure and tooling. Keep changes aligned with
that layout when restructuring.

## Commands

```bash
# Setup (src/ layout, editable install)
python3 -m venv venv_dolibarr && source venv_dolibarr/bin/activate
pip install -e '.[dev]'

# Run server (STDIO is default transport)
python -m dolibarr_mcp.dolibarr_mcp_server
MCP_TRANSPORT=http MCP_HTTP_PORT=8080 python -m dolibarr_mcp.dolibarr_mcp_server

# Verify Dolibarr credentials without an MCP host
python -m dolibarr_mcp.test_connection            # uses env vars
python -m dolibarr_mcp.test_connection --url https://.../api/index.php --api-key KEY

# Tests
pytest                              # all (pytest.ini_options forces --cov)
pytest -m "not integration"         # fast unit cycle — default while developing
pytest -m integration               # requires a real Dolibarr instance + credentials
pytest tests/test_search_tools.py::TestName::test_name   # single test
```

There is no lint pipeline. Match existing style; do not introduce one unprompted.

## Architecture

Two files hold almost all the logic:

- **`src/dolibarr_mcp/dolibarr_mcp_server.py`** (~1600 lines) — every MCP tool.
  Tool *schemas* live in `handle_list_tools()`; tool *dispatch* lives in
  `handle_call_tool()`. Adding/changing a tool means editing **both**. The tail
  of the file (`_run_stdio_server`, `_build_http_app`, `_run_http_server`, `main`)
  wires up STDIO vs. Starlette/Streamable-HTTP transports.
- **`src/dolibarr_mcp/dolibarr_client.py`** (~870 lines) — async aiohttp client.
  All HTTP goes through `_make_request()`, which handles retries (transient
  errors, `MAX_RETRIES`/`RETRY_BACKOFF_SECONDS`), payload validation
  (`_validate_payload`, `_apply_aliases`), and **structured error envelopes**
  (`_build_validation_error` → `validation_error`, `_build_internal_error` →
  `internal_error`). Keep that error shape stable — tests and callers depend on it.
- **`src/dolibarr_mcp/config.py`** — pydantic-settings `Config`. Reads env / `.env`.
  `DOLIBARR_URL`, `DOLIBARR_BASE_URL`, and `DOLIBARR_SHOP_URL` are all accepted
  aliases for the base URL, and the validator normalizes any of them to end in
  `/api/index.php`. Missing config warns to **stderr** and falls back to
  placeholders rather than crashing (so the server still starts).

## Conventions specific to this codebase

- **Specialized search tools, not generic getters.** Instead of one `get_products`
  that dumps everything, the server exposes `search_products_by_ref`,
  `search_products_by_label`, `resolve_product_ref`, `search_customers`,
  `search_projects`. These push filtering server-side via Dolibarr's `sqlfilters`
  to avoid loading thousands of records into the model's context. When adding a
  list-style tool, prefer this filtered pattern over a bulk fetch.
- **`sqlfilters` need escaping.** Use `_escape_sqlfilter()` (server) before
  interpolating user values into a `sqlfilters` string — single quotes must be
  escaped or the filter breaks / is injectable.
- **stdout must stay clean in STDIO mode.** All logging and diagnostics go to
  **stderr**; anything on stdout corrupts the MCP protocol stream.
- **Invoice lines come from a separate endpoint.** Invoice detail fetches the
  lines via a distinct API call (see the most recent commit) — don't assume the
  invoice object already contains them.
- **Reference autogen is opt-in.** `ALLOW_REF_AUTOGEN` / `REF_AUTOGEN_PREFIX`
  control whether missing `ref` fields are auto-generated.

## Adding or modifying a tool (checklist)

1. Update the schema in `handle_list_tools()`.
2. Update the `elif name == ...` branch in `handle_call_tool()`.
3. Add/adapt the method in `dolibarr_client.py`, reusing `_validate_payload`,
   the alias helpers, and the structured-error builders.
4. Add unit tests in `tests/` (mock `DolibarrClient` for server-level tests).
5. Run `pytest -m "not integration"` before finishing.

## Further docs

`AGENTS.md` covers playbooks and pitfalls. Deep dives live in `docs/`:
[configuration.md](docs/configuration.md), [api-reference.md](docs/api-reference.md),
[development.md](docs/development.md), [quickstart.md](docs/quickstart.md). Link to
these rather than duplicating their content here.
