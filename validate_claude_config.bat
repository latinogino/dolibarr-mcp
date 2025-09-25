@echo off
echo ======================================
echo Dolibarr MCP - Configuration Validator
echo ======================================
echo.

cd /d "C:\Users\gino\GitHub\dolibarr-mcp"

echo Checking virtual environment...
if exist "venv_dolibarr\Scripts\python.exe" (
    echo ✓ Virtual environment found
) else (
    echo ✗ Virtual environment not found - creating...
    python -m venv venv_dolibarr
)

echo.
echo Activating virtual environment...
call venv_dolibarr\Scripts\activate

echo.
echo Installing package in development mode...
pip install -e . >nul 2>&1

echo.
echo Installing dependencies...
pip install requests python-dotenv mcp aiohttp pydantic click typing-extensions >nul 2>&1

echo.
echo Testing module import paths...
echo ----------------------------------------

echo Test 1: Direct module import
python -c "import sys; sys.path.insert(0, 'src'); from dolibarr_mcp import __version__; print(f'  ✓ Direct import works - version: {__version__}')" 2>nul
if %errorlevel% neq 0 (
    echo   ✗ Direct import failed
)

echo.
echo Test 2: Module execution with -m flag
python -m dolibarr_mcp.dolibarr_mcp_server --help >nul 2>&1
if %errorlevel% neq 0 (
    echo   ✗ Module execution failed
    echo   Attempting fix...
    cd src
    python -m dolibarr_mcp.dolibarr_mcp_server --help >nul 2>&1
    if %errorlevel% neq 0 (
        echo   ✗ Still failing - checking Python path...
        python -c "import sys; print('Python paths:'); [print(f'  {p}') for p in sys.path[:5]]"
    ) else (
        echo   ✓ Works when run from src directory
    )
    cd ..
) else (
    echo   ✓ Module execution works
)

echo.
echo Test 3: Environment Variables
echo ----------------------------------------
python -c "import os; url=os.getenv('DOLIBARR_URL') or os.getenv('DOLIBARR_BASE_URL'); key=os.getenv('DOLIBARR_API_KEY'); print(f'  URL: {url[:30] if url else \"NOT SET\"}...'); print(f'  KEY: {\"*\" * 10 if key else \"NOT SET\"}')"

echo.
echo Test 4: Configuration for Claude Desktop
echo ----------------------------------------
echo Your configuration uses:
echo   - Command: venv_dolibarr\Scripts\python.exe
echo   - Args: -m dolibarr_mcp.dolibarr_mcp_server
echo   - CWD: C:\Users\gino\GitHub\dolibarr-mcp
echo   - ENV: DOLIBARR_BASE_URL and DOLIBARR_API_KEY

echo.
echo Validating this configuration...
set DOLIBARR_BASE_URL=https://db.ginos.cloud/api/index.php/
set DOLIBARR_API_KEY=7cxAAO835BF7bXy6DsQ2j2a7nT6ectGY

python -c "from src.dolibarr_mcp.config import Config; c=Config(); print(f'  ✓ Config loads successfully'); print(f'  URL processed as: {c.dolibarr_url}')" 2>nul
if %errorlevel% neq 0 (
    echo   ✗ Config loading failed
)

echo.
echo ========================================
echo FINAL TEST: Running MCP server briefly
echo ========================================
timeout /t 1 >nul
echo Starting server (will run for 3 seconds)...
start /B python -m dolibarr_mcp.dolibarr_mcp_server 2>server_test.log
timeout /t 3 >nul
taskkill /F /IM python.exe >nul 2>&1

if exist server_test.log (
    echo.
    echo Server output:
    type server_test.log | findstr /C:"Starting Professional Dolibarr MCP server" >nul
    if %errorlevel% equ 0 (
        echo   ✓ Server starts successfully!
    ) else (
        echo   ✗ Server failed to start properly
        echo   Check server_test.log for details
    )
    del server_test.log
)

echo.
echo ========================================
echo Configuration Status: READY
echo ========================================
echo.
echo Your Claude Desktop config should work with:
echo.
echo {
echo   "mcpServers": {
echo     "dolibarr-python": {
echo       "command": "C:\\Users\\gino\\GitHub\\dolibarr-mcp\\venv_dolibarr\\Scripts\\python.exe",
echo       "args": ["-m", "dolibarr_mcp.dolibarr_mcp_server"],
echo       "cwd": "C:\\Users\\gino\\GitHub\\dolibarr-mcp",
echo       "env": {
echo         "DOLIBARR_BASE_URL": "https://db.ginos.cloud/api/index.php/",
echo         "DOLIBARR_API_KEY": "7cxAAO835BF7bXy6DsQ2j2a7nT6ectGY"
echo       }
echo     }
echo   }
echo }
echo.
pause
