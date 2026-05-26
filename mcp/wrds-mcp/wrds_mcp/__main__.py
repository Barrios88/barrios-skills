"""Allow running as `python -m wrds_mcp`."""
from wrds_mcp.server import mcp

if __name__ == "__main__":
    mcp.run()
