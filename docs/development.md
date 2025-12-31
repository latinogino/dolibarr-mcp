# Development

This project uses the same lightweight tooling philosophy as `prestashop-mcp`.
The code lives under `src/`, tests under `tests/` and optional Docker assets are
kept separate in `docker/`.

## Install development dependencies

It is recommended to use a virtual environment to avoid conflicts with system packages (especially on Linux systems with externally managed environments).

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate  # On Linux/macOS
# .venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

## Run the test suite

Once your virtual environment is active:

```bash
pytest
```

To gather coverage metrics:

```bash
pytest --cov=src/dolibarr_mcp --cov-report=term-missing
```

If you encounter "command not found" errors, ensure your virtual environment is activated or run via python module:

```bash
python3 -m pytest
```

### Integration tests

The suite includes a small number of `@pytest.mark.integration` tests that hit a
real Dolibarr instance. They are skipped by default unless valid credentials are
present. To run them:

```bash
export DOLIBARR_URL="https://your-dolibarr.example.com/api/index.php"
export DOLIBARR_API_KEY="your-api-key"
pytest -m integration
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
