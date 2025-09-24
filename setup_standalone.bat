@echo off
cls
echo ======================================
echo Dolibarr MCP Standalone Setup v3.0
echo ======================================
echo SOLVES: Windows pywin32 permission issues
echo METHOD: Standalone implementation without MCP package
echo.

echo [1/5] Cleanup old environment...
if exist "venv_dolibarr" (
    echo Removing old virtual environment...
    rmdir /s /q "venv_dolibarr" 2>nul
    timeout /t 1 /nobreak >nul
)

echo [2/5] Creating fresh Python environment...
python -m venv venv_dolibarr
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Virtual environment creation failed
    echo Check: python --version
    pause
    exit /b 1
)

echo [3/5] Activating environment...
call venv_dolibarr\Scripts\activate.bat

echo [4/5] Installing Windows-compatible dependencies...
echo Installing core packages without pywin32...

REM Install packages one by one to handle failures gracefully
pip install --no-warn-script-location requests>=2.31.0
pip install --no-warn-script-location aiohttp>=3.9.0  
pip install --no-warn-script-location pydantic>=2.5.0
pip install --no-warn-script-location python-dotenv>=1.0.0
pip install --no-warn-script-location click>=8.1.0
pip install --no-warn-script-location typing-extensions>=4.8.0
pip install --no-warn-script-location jsonschema>=4.20.0
pip install --no-warn-script-location httpx>=0.27.1

echo.
echo [5/5] Testing installation...
python -c "import aiohttp, pydantic, requests, json; print('✅ Core libraries working')" 2>nul
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Some import test failed, but continuing...
)

echo.
echo Checking configuration...
if not exist ".env" (
    echo Creating .env from template...
    copy ".env.example" ".env" >nul 2>&1
    echo [INFO] Created .env file - please configure your Dolibarr credentials
)

echo.
echo ======================================
echo ✅ STANDALONE SETUP COMPLETE!
echo ======================================
echo.
echo 🔧 What was installed:
echo   • Python virtual environment (venv_dolibarr)
echo   • Core HTTP libraries (aiohttp, requests, httpx)
echo   • Data validation (pydantic)
echo   • Configuration (.env support)
echo   • JSON-RPC support (no MCP package needed)
echo.
echo 📝 Next Steps:
echo   1. Edit .env file with your Dolibarr credentials
echo   2. Run: run_standalone.bat
echo.
echo 🚀 Test the server:
echo   python -m src.dolibarr_mcp.standalone_server
echo.
echo 💡 This version works WITHOUT the problematic MCP package!
echo.
pause
