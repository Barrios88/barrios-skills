"""WRDS MCP Server — Model Context Protocol server for Wharton Research Data Services.

Provides 16 tools for exploring WRDS schemas, running SQL queries, downloading
data, and common research workflows (CRSP, Compustat, IBES, Fama-French,
13F holdings, Audit Analytics, ExecuComp, PitchBook, Revelio Labs).

Usage:
    # As an MCP server (stdio transport)
    python -m wrds_mcp.server

    # Or via the installed entry point
    wrds-mcp

Environment variables:
    WRDS_USERNAME: Your WRDS username
    WRDS_PASSWORD: Your WRDS password
    WRDS_DOWNLOAD_DIR: Directory for downloaded files (default: ~/wrds_data)
"""

__version__ = "0.1.0"
