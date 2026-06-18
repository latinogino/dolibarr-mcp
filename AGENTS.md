# AGENTS.md

Agent instructions for productive work in this repository.

## Project Snapshot

- Python MCP server for Dolibarr ERP/CRM.
- Main flow: MCP server tools -> `DolibarrClient` -> Dolibarr REST API.
- Core paths:
  - `src/dolibarr_mcp/dolibarr_mcp_server.py` (tool schemas + dispatch)
  - `src/dolibarr_mcp/dolibarr_client.py` (HTTP client, validation, retries)
  - `src/dolibarr_mcp/config.py` (env-driven settings)

## Fast Commands

- Setup:
  - `python3 -m venv venv_dolibarr`
  - `source venv_dolibarr/bin/activate`
  - `pip install -e .`
  - `pip install -e '.[dev]'`
- Run MCP server (STDIO):
  - `python -m dolibarr_mcp.dolibarr_mcp_server`
- Run MCP server (HTTP):
  - `MCP_TRANSPORT=http MCP_HTTP_PORT=8080 python -m dolibarr_mcp.dolibarr_mcp_server`
- Tests:
  - `pytest`
  - `pytest -m "not integration"`
  - `pytest -m integration` (requires valid Dolibarr credentials)
  - `pytest --cov=src/dolibarr_mcp --cov-report=term-missing`

## Non-Negotiable Conventions

- Keep stdout clean in server mode; logging must not break MCP protocol.
- Keep changes minimal and scoped; do not refactor unrelated areas.
- Follow current style; repository intentionally has no heavy lint pipeline.
- Never log secrets (API keys, tokens).
- Use existing docs as source of truth; link rather than duplicating details.

## Common Change Playbooks

### Add or modify an MCP tool

1. Update tool definition in `handle_list_tools()` (`src/dolibarr_mcp/dolibarr_mcp_server.py`).
2. Update tool dispatch in `handle_call_tool()` (`src/dolibarr_mcp/dolibarr_mcp_server.py`).
3. Add or adapt client method in `src/dolibarr_mcp/dolibarr_client.py`.
4. Add/adjust tests in `tests/` (unit first, integration only where needed).
5. Run `pytest -m "not integration"` before finishing.

### Add API payload fields

- Validate through client-side validation helpers before request dispatch.
- Preserve existing alias/required-field patterns in `dolibarr_client.py`.
- Keep structured error format stable (`validation_error` / `internal_error`).

## Testing Guidance

- Default: fast unit test cycle via `pytest -m "not integration"`.
- Integration tests are credential-dependent and may be skipped in CI/local runs.
- For tool-level behavior, prefer mocking `DolibarrClient` in server tests.

## Pitfalls

- SQL filter terms must escape single quotes before building `sqlfilters`.
- Ensure environment uses API URL form expected by docs (`.../api/index.php`).
- HTTP transport requires `MCP_TRANSPORT=http`; default is STDIO.

## Documentation Map (link, do not duplicate)

- Overview and usage: [README.md](README.md)
- Docs index: [docs/README.md](docs/README.md)
- Configuration details: [docs/configuration.md](docs/configuration.md)
- API/tool behavior: [docs/api-reference.md](docs/api-reference.md)
- Development and debugging: [docs/development.md](docs/development.md)
- Quick local startup: [docs/quickstart.md](docs/quickstart.md)

## Optional Improvement Areas

- Split large server dispatch into smaller modules when doing major feature work.
- Add focused tests whenever touching invoice/project/search tool behavior.
