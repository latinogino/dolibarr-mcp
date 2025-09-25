# Cleanup Plan for Dolibarr MCP

## Files to be REMOVED

### Test Scripts in Root Directory (to be removed)
- `test_api_connection.py`
- `test_api_debug.py`
- `test_connection.py`
- `test_dolibarr_mcp.py`
- `test_install.py`
- `test_standalone.py`
- `test_ultra.py`
- `test_ultra_direct.py`
- `diagnose_and_fix.py`

### Batch Files (to be consolidated/removed)
- `cleanup.bat`
- `fix_installation.bat`
- `run_dolibarr_mcp.bat`
- `run_server.bat`
- `run_standalone.bat`
- `run_ultra.bat`
- `setup.bat`
- `setup_claude_complete.bat`
- `setup_manual.bat`
- `setup_standalone.bat`
- `setup_ultra.bat`
- `setup_windows_fix.bat`
- `start_server.bat`
- `validate_claude_config.bat`

### Python Scripts in Root (to be removed)
- `mcp_server_launcher.py`
- `setup_env.py`

### Alternative Server Implementations (to be removed from src/)
- `src/dolibarr_mcp/simple_client.py`
- `src/dolibarr_mcp/standalone_server.py`
- `src/dolibarr_mcp/ultra_simple_server.py`

### Multiple Requirements Files (to be consolidated)
- `requirements-minimal.txt`
- `requirements-ultra-minimal.txt`
- `requirements-windows.txt`
(Keep only `requirements.txt`)

### Documentation Files (to be removed)
- `README_DE.md`
- `CLAUDE_CONFIG.md`
- `CONFIG_COMPATIBILITY.md`
- `MCP_FIX_GUIDE.md`
- `ULTRA-SOLUTION.md`

### API Directory (to be removed)
- `api/` directory and all its contents

## Files to KEEP (matching prestashop-mcp structure)

### Root Directory
- `.env.example`
- `.gitignore`
- `LICENSE`
- `README.md` (already updated)
- `CHANGELOG.md`
- `pyproject.toml`
- `requirements.txt`
- `Dockerfile`
- `docker-compose.yml`
- `setup.py`
- `setup.sh`

### Source Directory
- `src/dolibarr_mcp/__init__.py`
- `src/dolibarr_mcp/__main__.py`
- `src/dolibarr_mcp/cli.py`
- `src/dolibarr_mcp/config.py`
- `src/dolibarr_mcp/dolibarr_client.py`
- `src/dolibarr_mcp/dolibarr_mcp_server.py`

### Tests Directory
- `tests/__init__.py`
- `tests/test_dolibarr_client.py`
- Tests will be restructured to match prestashop-mcp pattern

## Next Steps

1. Remove all files listed above
2. Update pyproject.toml to match prestashop-mcp structure
3. Update requirements.txt to contain only necessary dependencies
4. Create proper test structure in tests/ directory
5. Update .gitignore to match prestashop-mcp
6. Update CHANGELOG.md to document the restructuring

## Goal

Create a clean, maintainable structure that matches the prestashop-mcp reference implementation.
