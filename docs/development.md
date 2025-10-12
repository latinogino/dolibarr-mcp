# Development

This project uses the same lightweight tooling philosophy as `prestashop-mcp`.
The code lives under `src/`, tests under `tests/` and optional Docker assets are
kept separate in `docker/`.

## Install development dependencies

```bash
pip install -e '.[dev]'
```

### Windows PowerShell

```powershell
pip install -e .`[dev`]
```

## Run the test suite

```bash
pytest
```

To gather coverage metrics:

```bash
pytest --cov=src/dolibarr_mcp --cov-report=term-missing
```

## Formatting and linting

The project intentionally avoids heavy linting dependencies. Follow the coding
style already present in the repository and run the test-suite before opening a
pull request.

## Docker tooling

Container assets live in `docker/`:

- `Dockerfile` – production-ready image for the MCP server
- `docker-compose.yml` – local stack that spins up Dolibarr together with the MCP server

Build and run the container locally with:

```bash
docker compose -f docker/docker-compose.yml up --build
```
