# Claude Desktop MCP Configuration for Dolibarr

## Installation Instructions

1. First run the installation fix:
   ```
   fix_installation.bat
   ```

2. Add to your Claude Desktop config file (`%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "dolibarr-python": {
      "command": "python",
      "args": [
        "C:\\Users\\[YOUR_USERNAME]\\GitHub\\dolibarr-mcp\\mcp_server_launcher.py"
      ],
      "env": {
        "DOLIBARR_URL": "https://your-dolibarr-instance.com/api/index.php",
        "DOLIBARR_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Alternative Configuration (if above doesn't work):

```json
{
  "mcpServers": {
    "dolibarr-python": {
      "command": "C:\\Users\\[YOUR_USERNAME]\\GitHub\\dolibarr-mcp\\venv_dolibarr\\Scripts\\python.exe",
      "args": [
        "-m", 
        "dolibarr_mcp"
      ],
      "cwd": "C:\\Users\\[YOUR_USERNAME]\\GitHub\\dolibarr-mcp"
    }
  }
}
```

## Troubleshooting

1. **Module not found error**: Run `fix_installation.bat`
2. **API connection error**: Check your `.env` file has correct credentials
3. **Server doesn't start**: Try running `python mcp_server_launcher.py` manually to see errors

## Testing the Server

After configuration, restart Claude Desktop and check if the server is listed in available MCP servers.

You can test with commands like:
- "Test Dolibarr connection"
- "List Dolibarr users"
- "Show Dolibarr products"
