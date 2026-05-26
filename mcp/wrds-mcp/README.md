# WRDS MCP Server

> Part of [Barrios Skills](../../README.md). **Full setup:** [install/wrds-mcp.md](../../install/wrds-mcp.md) — includes your WRDS username/password and Duo tunnel workflow.


MCP (Model Context Protocol) server for [WRDS](https://wrds-www.wharton.upenn.edu/) — Wharton Research Data Services.

## Features

- **Schema exploration**: List libraries, tables, describe columns
- **SQL queries**: Run read-only SQL against WRDS
- **Data download**: Export to CSV, Parquet, or JSON
- **Smart tools**: Pre-built queries for CRSP returns, Compustat fundamentals, and CRSP-Compustat merges
- **SSH tunnel**: Bypasses WRDS MFA by tunneling through wrds-cloud

## Prerequisites

- WRDS account with active subscription
- `sshpass` installed (`brew install sshpass` on Mac, `apt install sshpass` on Linux)
- Python 3.10+

## Setup

```bash
# Install
pip install -e .

# Set credentials
export WRDS_USERNAME="your_username"
export WRDS_PASSWORD="your_password"

# Optional: set download directory (default: ~/wrds_data)
export WRDS_DOWNLOAD_DIR="/path/to/downloads"
```

## Usage with Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "wrds": {
      "command": "python",
      "args": ["-m", "wrds_mcp.server"],
      "env": {
        "WRDS_USERNAME": "your_username",
        "WRDS_PASSWORD": "your_password"
      }
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `wrds_list_libraries` | List all WRDS database schemas |
| `wrds_list_tables` | List tables within a library |
| `wrds_describe_table` | Describe columns and row count |
| `wrds_sample_data` | Preview sample rows |
| `wrds_run_sql` | Execute read-only SQL queries |
| `wrds_download_data` | Download data to CSV/Parquet/JSON |
| `wrds_get_crsp_returns` | Fetch CRSP daily/monthly returns |
| `wrds_get_compustat` | Fetch Compustat annual/quarterly data |
| `wrds_merge_crsp_compustat` | Merge CRSP + Compustat via CCM |
