# WRDS MCP quick reference

Full guide: [install/wrds-mcp.md](../../../../install/wrds-mcp.md)

## Your credentials (required)

```bash
export WRDS_USERNAME="your_wrds_username"   # from WRDS account registration
export WRDS_PASSWORD="your_wrds_password"   # never commit or share
```

## Session startup

```bash
bash mcp/wrds-mcp/tunnel/tunnel_up.sh   # approve Duo Push once
```

## MCP env (Cursor / Claude)

```json
{
  "WRDS_USERNAME": "your_wrds_username",
  "WRDS_PASSWORD": "your_wrds_password",
  "WRDS_TUNNEL_PORT": "49600"
}
```

## Shutdown

```bash
bash mcp/wrds-mcp/tunnel/tunnel_down.sh
```
