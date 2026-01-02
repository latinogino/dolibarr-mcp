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

## Debugging 500 responses with correlation IDs

Unexpected Dolibarr API failures return a `correlation_id` in the JSON body.
Include this value when filing issues or investigating user reports.

1. Capture the `correlation_id` from the HTTP 500 response body.
2. Search the MCP server logs (stdout/stderr) for that ID to locate the full
   stack trace. For docker users:

   ```bash
   docker logs <container> 2>&1 | grep "<correlation_id>"
   ```

3. The log entry contains the failing endpoint and sanitized payload details.
   Avoid logging `DOLAPIKEY` or other secrets in bug reports.

## Docker tooling

Container assets live in `docker/`:

- `Dockerfile` – production-ready image for the MCP server
- `docker-compose.yml` – local stack that spins up Dolibarr together with the MCP server

Build and run the container locally with:

```bash
docker compose -f docker/docker-compose.yml up --build
```
