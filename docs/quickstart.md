# Quickstart

Follow these steps to install and run the Dolibarr MCP server. The process
mirrors the streamlined developer experience of the `prestashop-mcp` project.

## 1. Clone the repository

```bash
git clone https://github.com/latinogino/dolibarr-mcp.git
cd dolibarr-mcp
```

## 2. Create a virtual environment

### Linux / macOS

```bash
python3 -m venv venv_dolibarr
source venv_dolibarr/bin/activate
```

### Windows (PowerShell)

```powershell
py -3 -m venv venv_dolibarr
./venv_dolibarr/Scripts/Activate.ps1
```

## 3. Install the package

```bash
pip install -e .
```

For development and testing utilities add the optional extras:

```bash
pip install -e '.[dev]'
```

On Windows escape the brackets inside PowerShell:

```powershell
pip install -e .`[dev`]
```

## 4. Configure credentials

Create a `.env` file in the project root (see
[`configuration.md`](configuration.md)) or export the variables within your MCP
host application.

## 5. Run the server

```bash
python -m dolibarr_mcp.dolibarr_mcp_server
```

The command starts the STDIO based MCP server that Claude Desktop and other
clients can communicate with. When wiring the server into Claude Desktop, set
`command` to the path returned by `Get-Command python` (Windows PowerShell) or
`which python` (Linux/macOS) while the virtual environment is activated, and use
the arguments `-m dolibarr_mcp.dolibarr_mcp_server`.

## 6. (Optional) Test the connection

Verify the credentials before integrating the server with Claude Desktop:

```bash
python -m dolibarr_mcp.test_connection
```

Override the URL or API key directly when needed:

```bash
python -m dolibarr_mcp.test_connection --url https://your-dolibarr.example.com/api/index.php --api-key YOUR_API_KEY
```

