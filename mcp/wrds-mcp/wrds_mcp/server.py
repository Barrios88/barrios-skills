#!/usr/bin/env python3
"""
WRDS MCP Server — Model Context Protocol server for Wharton Research Data Services.

Connects to WRDS via SSH tunnel (bypassing MFA for subsequent PostgreSQL access),
then exposes tools for exploring schemas, querying data, and downloading datasets.

Authentication: Set WRDS_USERNAME and WRDS_PASSWORD as environment variables.
"""

import asyncio
import json
import os
import io
import time
import logging
import subprocess
import signal
import socket
import shutil
import threading
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from enum import Enum

import pandas as pd
import sqlalchemy as sa
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP, Context

# Optional: paramiko for environments without sshpass
try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger("wrds_mcp")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
logger.addHandler(handler)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
WRDS_SSH_HOST = "wrds-cloud.wharton.upenn.edu"
WRDS_PG_HOST = "wrds-pgdata.wharton.upenn.edu"
WRDS_PG_PORT = 9737
WRDS_PG_DB = "wrds"

MAX_ROWS_DEFAULT = 1000
MAX_ROWS_LIMIT = 100_000
DOWNLOAD_DIR = os.environ.get("WRDS_DOWNLOAD_DIR", os.path.expanduser("~/wrds_data"))

# ---------------------------------------------------------------------------
# SSH Tunnel Manager — supports both sshpass and paramiko
# ---------------------------------------------------------------------------
# Priority: sshpass (fast, no MFA needed if .pgpass configured) > paramiko (Duo MFA)

class SSHTunnelSSHPass:
    """SSH tunnel using sshpass (simplest, works when sshpass is installed)."""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.local_port: Optional[int] = None
        self._process: Optional[subprocess.Popen] = None

    def _find_free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]

    def start(self) -> int:
        if self._process and self._process.poll() is None:
            return self.local_port

        self.local_port = self._find_free_port()
        cmd = [
            "sshpass", "-p", self.password,
            "ssh", "-N",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "ServerAliveInterval=60",
            "-L", f"{self.local_port}:{WRDS_PG_HOST}:{WRDS_PG_PORT}",
            f"{self.username}@{WRDS_SSH_HOST}"
        ]
        self._process = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
        )
        time.sleep(3)
        if self._process.poll() is not None:
            stderr = self._process.stderr.read().decode() if self._process.stderr else ""
            raise ConnectionError(f"sshpass SSH tunnel failed: {stderr}")
        logger.info(f"SSH tunnel (sshpass) on local port {self.local_port}")
        return self.local_port

    def stop(self):
        if self._process and self._process.poll() is None:
            self._process.send_signal(signal.SIGTERM)
            self._process.wait(timeout=5)
            logger.info("SSH tunnel (sshpass) closed")


class SSHTunnelParamiko:
    """SSH tunnel using paramiko — handles WRDS Duo MFA via keyboard-interactive.

    Automatically sends 'push' when Duo prompts, triggering a Duo Push
    notification on your phone. You must approve it within ~30 seconds.
    """

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.local_port: Optional[int] = None
        self._transport = None
        self._server_socket: Optional[socket.socket] = None
        self._running = False

    def _find_free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]

    def _ki_handler(self, title, instructions, prompt_list):
        responses = []
        for prompt_text, echo in prompt_list:
            p = prompt_text.lower().strip()
            if "password" in p:
                responses.append(self.password)
            elif "passcode" in p or "duo" in p or "option" in p:
                logger.info("Duo MFA triggered — sending push. Approve on your phone!")
                responses.append("push")
            else:
                responses.append(self.password)
        return responses

    def _tunnel_loop(self):
        while self._running:
            try:
                client_sock, addr = self._server_socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            try:
                channel = self._transport.open_channel(
                    "direct-tcpip", (WRDS_PG_HOST, WRDS_PG_PORT), addr
                )
                # Bidirectional forwarding
                for src, dst in [(client_sock, channel), (channel, client_sock)]:
                    threading.Thread(target=self._fwd, args=(src, dst), daemon=True).start()
            except Exception as e:
                logger.warning(f"Tunnel channel failed: {e}")
                client_sock.close()

    @staticmethod
    def _fwd(src, dst):
        try:
            while True:
                data = src.recv(4096)
                if not data:
                    break
                dst.sendall(data)
        except Exception:
            pass
        try:
            dst.close()
        except Exception:
            pass

    def start(self) -> int:
        if self._transport and self._transport.is_active():
            return self.local_port

        import paramiko as _paramiko
        self._transport = _paramiko.Transport((WRDS_SSH_HOST, 22))
        self._transport.connect()
        self._transport.auth_interactive(self.username, self._ki_handler)

        if not self._transport.is_authenticated():
            raise ConnectionError(
                "WRDS SSH auth failed. Check credentials and approve Duo Push."
            )
        logger.info("SSH authenticated to WRDS (Duo MFA approved)")

        self.local_port = self._find_free_port()
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind(("127.0.0.1", self.local_port))
        self._server_socket.listen(5)
        self._server_socket.settimeout(1)

        self._running = True
        threading.Thread(target=self._tunnel_loop, daemon=True).start()
        logger.info(f"SSH tunnel (paramiko) on 127.0.0.1:{self.local_port}")
        return self.local_port

    def stop(self):
        self._running = False
        if self._server_socket:
            try: self._server_socket.close()
            except Exception: pass
        if self._transport:
            try: self._transport.close()
            except Exception: pass
        logger.info("SSH tunnel (paramiko) closed")


def create_tunnel(username: str, password: str):
    """Create the best available SSH tunnel.

    WRDS-cloud bastion requires keyboard-interactive auth (Duo MFA), so paramiko
    is preferred. sshpass only works on hosts that accept plain password auth —
    set WRDS_USE_SSHPASS=true to force it.
    """
    use_sshpass = os.environ.get("WRDS_USE_SSHPASS", "").lower() in ("true", "1", "yes")

    if HAS_PARAMIKO and not use_sshpass:
        logger.info("Using paramiko for SSH tunnel (handles WRDS Duo MFA)")
        return SSHTunnelParamiko(username, password)
    elif shutil.which("sshpass"):
        logger.info("Using sshpass for SSH tunnel (WRDS_USE_SSHPASS or paramiko unavailable)")
        return SSHTunnelSSHPass(username, password)
    elif HAS_PARAMIKO:
        logger.info("Using paramiko for SSH tunnel")
        return SSHTunnelParamiko(username, password)
    else:
        raise EnvironmentError(
            "Neither paramiko nor sshpass is available. "
            "Install paramiko (recommended): 'pip install paramiko'"
        )

# ---------------------------------------------------------------------------
# Database Connection
# ---------------------------------------------------------------------------
class WRDSConnection:
    """Wraps SQLAlchemy engine connected to WRDS PostgreSQL.

    Supports two modes:
    - tunnel mode: connects through an SSH tunnel (set tunnel param)
    - direct mode: connects directly to wrds-pgdata.wharton.upenn.edu:9737
      (requires .pgpass file or WRDS_DIRECT=true env var; skips Duo MFA)
    """

    def __init__(self, username: str, password: str, tunnel=None, external_port: Optional[int] = None):
        self.tunnel = tunnel
        self.username = username
        self.password = password
        self.external_port = external_port
        self.engine: Optional[sa.engine.Engine] = None

    def connect(self):
        if self.tunnel:
            # Connect through SSH tunnel managed in-process
            local_port = self.tunnel.start()
            url = (
                f"postgresql+psycopg2://{self.username}:{self.password}"
                f"@127.0.0.1:{local_port}/{WRDS_PG_DB}"
            )
            logger.info("Connecting to WRDS PostgreSQL via in-process SSH tunnel...")
        elif self.external_port:
            # Connect through an externally-managed tunnel (e.g., tunnel_daemon.py)
            url = (
                f"postgresql+psycopg2://{self.username}:{self.password}"
                f"@127.0.0.1:{self.external_port}/{WRDS_PG_DB}"
            )
            logger.info(f"Connecting to WRDS PostgreSQL via external tunnel on 127.0.0.1:{self.external_port}...")
        else:
            # Connect directly (requires .pgpass or network access without MFA)
            url = (
                f"postgresql+psycopg2://{self.username}:{self.password}"
                f"@{WRDS_PG_HOST}:{WRDS_PG_PORT}/{WRDS_PG_DB}"
            )
            logger.info("Connecting directly to WRDS PostgreSQL (no SSH tunnel)...")

        self.engine = sa.create_engine(
            url, pool_pre_ping=True, pool_size=3,
            connect_args={"connect_timeout": 30, "sslmode": "require"}
        )
        # Quick connectivity check
        with self.engine.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
        mode = "SSH tunnel" if self.tunnel else "direct"
        logger.info(f"Connected to WRDS PostgreSQL ({mode})")

    def execute(self, sql: str, params: Optional[dict] = None) -> pd.DataFrame:
        if not self.engine:
            raise ConnectionError("Not connected. Call connect() first.")
        with self.engine.connect() as conn:
            return pd.read_sql(sa.text(sql), conn, params=params)

    def close(self):
        if self.engine:
            self.engine.dispose()
        if self.tunnel:
            self.tunnel.stop()

# ---------------------------------------------------------------------------
# Lazy Connection Manager — connects on first tool call, not at startup
# ---------------------------------------------------------------------------
# Set WRDS_DIRECT=true to skip SSH tunnel and connect directly.
# Direct mode requires network access to WRDS PostgreSQL without MFA.

class LazyWRDSConnection:
    """Defers WRDS connection until the first tool actually needs it.

    This lets the MCP server start instantly and register its tools.
    The actual PostgreSQL connection (and optional SSH tunnel + Duo MFA)
    only happens when you invoke a tool for the first time.

    All blocking I/O (SSH tunnel, PostgreSQL queries) runs in a background
    thread via asyncio.to_thread so it never blocks the MCP event loop.
    """

    def __init__(self):
        self._db: Optional[WRDSConnection] = None
        self._connected = False
        self._lock = threading.Lock()

    def _tunnel_alive(self) -> bool:
        """Check whether the tunnel (in-process or external) is still alive."""
        if not self._db:
            return True
        # External tunnel: probe the local port — if the daemon's listener is
        # still bound but its SSH transport died, we can't tell from here. The
        # OperationalError retry path in _execute_sync handles that case.
        if self._db.external_port:
            return self._external_port_open(self._db.external_port)
        if not self._db.tunnel:
            return True  # Direct mode
        t = self._db.tunnel
        if hasattr(t, "_process") and t._process is not None:
            return t._process.poll() is None
        if hasattr(t, "_transport") and t._transport is not None:
            try:
                return t._transport.is_active()
            except Exception:
                return False
        return False

    def _external_port_open(self, port: int) -> bool:
        """Probe the external tunnel port to verify it's listening."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect(("127.0.0.1", port))
                return True
        except Exception:
            return False

    def _force_reconnect(self):
        """Tear down current connection so the next _ensure_connected_sync rebuilds."""
        try:
            if self._db:
                self._db.close()
        except Exception:
            pass
        self._db = None
        self._connected = False

    def _ensure_connected_sync(self):
        """Synchronous connection setup — runs in a thread."""
        with self._lock:
            # If we think we're connected, verify the tunnel is still alive.
            # If not, tear down and reconnect (one Duo prompt for paramiko).
            if self._connected and not self._tunnel_alive():
                if self._db and self._db.external_port:
                    logger.warning("External tunnel daemon unreachable — will reconnect")
                else:
                    logger.warning("SSH tunnel died — reconnecting")
                self._force_reconnect()

            if self._connected:
                return

            username = os.environ.get("WRDS_USERNAME", "")
            password = os.environ.get("WRDS_PASSWORD", "")
            if not username or not password:
                raise EnvironmentError(
                    "WRDS_USERNAME and WRDS_PASSWORD environment variables are required."
                )

            use_direct = os.environ.get("WRDS_DIRECT", "").lower() in ("true", "1", "yes")
            external_port_env = os.environ.get("WRDS_TUNNEL_PORT", "").strip()

            if external_port_env:
                # External tunnel: assume tunnel_daemon.py (or equivalent) is forwarding
                # 127.0.0.1:$WRDS_TUNNEL_PORT to wrds-pgdata. No in-process SSH, no Duo.
                try:
                    external_port = int(external_port_env)
                except ValueError:
                    raise EnvironmentError(f"WRDS_TUNNEL_PORT='{external_port_env}' is not an integer.")
                if not self._external_port_open(external_port):
                    raise ConnectionError(
                        f"WRDS_TUNNEL_PORT={external_port} is set but nothing is listening on "
                        f"127.0.0.1:{external_port}. Start the tunnel daemon "
                        f"(e.g., bash build/code/tunnel_up.sh) before invoking wrds-mcp."
                    )
                logger.info(f"Using external tunnel on 127.0.0.1:{external_port}")
                self._db = WRDSConnection(username, password, external_port=external_port)
            elif use_direct:
                logger.info("Direct mode (WRDS_DIRECT=true) — connecting without SSH tunnel...")
                self._db = WRDSConnection(username, password, tunnel=None)
            else:
                logger.info("Tunnel mode — setting up in-process SSH connection...")
                tunnel = create_tunnel(username, password)
                self._db = WRDSConnection(username, password, tunnel=tunnel)

            self._db.connect()
            self._connected = True

    def _execute_sync(self, sql: str, params: Optional[dict] = None) -> pd.DataFrame:
        """Synchronous query — runs in a thread.

        Auto-reconnects once on OperationalError (covers the case where the
        external tunnel daemon's SSH transport died but its local listener is
        still bound — the connect probe in _tunnel_alive can't catch that).
        """
        self._ensure_connected_sync()
        try:
            return self._db.execute(sql, params)
        except sa.exc.OperationalError as e:
            logger.warning("query OperationalError (%s) — forcing reconnect and retrying once", e)
            with self._lock:
                self._force_reconnect()
            self._ensure_connected_sync()
            return self._db.execute(sql, params)

    async def execute(self, sql: str, params: Optional[dict] = None) -> pd.DataFrame:
        """Async wrapper: runs blocking DB call in a background thread."""
        return await asyncio.to_thread(self._execute_sync, sql, params)

    def close(self):
        if self._db:
            self._db.close()


# ---------------------------------------------------------------------------
# Module-level globals — simpler than lifespan state, works across MCP versions
# ---------------------------------------------------------------------------
_db = LazyWRDSConnection()
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Initialize MCP
# ---------------------------------------------------------------------------
mcp = FastMCP("wrds_mcp")

# ---------------------------------------------------------------------------
# Helper: get DB and download dir
# ---------------------------------------------------------------------------
def _get_db(ctx=None):
    return _db

def _get_download_dir(ctx=None) -> str:
    return DOWNLOAD_DIR

# ---------------------------------------------------------------------------
# Enums & Shared Models
# ---------------------------------------------------------------------------
class ExportFormat(str, Enum):
    CSV = "csv"
    PARQUET = "parquet"
    JSON = "json"  # in-memory, returned as text

class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"

# ============================================================================
# CORE TOOLS — Schema Exploration
# ============================================================================

class ListLibrariesInput(BaseModel):
    """Input for listing WRDS libraries (schemas)."""
    model_config = ConfigDict(str_strip_whitespace=True)
    filter: Optional[str] = Field(
        default=None,
        description="Optional substring filter on library names (e.g., 'comp', 'crsp')"
    )

@mcp.tool(
    name="wrds_list_libraries",
    annotations={
        "title": "List WRDS Libraries",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def wrds_list_libraries(params: ListLibrariesInput, ctx: Context) -> str:
    """List all available WRDS data libraries (database schemas).

    Returns the names of all schemas accessible with your WRDS subscription.
    Use the optional filter to narrow results (e.g., filter='crsp' to find
    CRSP-related libraries).

    Args:
        params: filter (Optional[str]) — substring to match against library names

    Returns:
        Markdown-formatted list of library names, or JSON array.
    """
    db = _get_db(ctx)
    sql = """
        SELECT DISTINCT table_schema
        FROM information_schema.tables
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY table_schema
    """
    df = await db.execute(sql)
    libraries = df["table_schema"].tolist()

    if params.filter:
        libraries = [lib for lib in libraries if params.filter.lower() in lib.lower()]

    if not libraries:
        return "No libraries found matching your filter."

    lines = [f"# WRDS Libraries ({len(libraries)} found)", ""]
    for lib in libraries:
        lines.append(f"- `{lib}`")
    lines.append("")
    lines.append("Use `wrds_list_tables` to explore tables within a library.")
    return "\n".join(lines)


class ListTablesInput(BaseModel):
    """Input for listing tables within a WRDS library."""
    model_config = ConfigDict(str_strip_whitespace=True)
    library: str = Field(
        ..., description="WRDS library/schema name (e.g., 'comp', 'crsp', 'ibes')",
        min_length=1, max_length=100
    )
    filter: Optional[str] = Field(
        default=None, description="Optional substring filter on table names"
    )

@mcp.tool(
    name="wrds_list_tables",
    annotations={
        "title": "List Tables in a WRDS Library",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def wrds_list_tables(params: ListTablesInput, ctx: Context) -> str:
    """List all tables within a specific WRDS library.

    Args:
        params: library (str) — the schema name; filter (Optional[str]) — substring match

    Returns:
        Markdown list of table names in the library.
    """
    db = _get_db(ctx)
    sql = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = :schema
        ORDER BY table_name
    """
    df = await db.execute(sql, {"schema": params.library.lower()})
    tables = df["table_name"].tolist()

    if params.filter:
        tables = [t for t in tables if params.filter.lower() in t.lower()]

    if not tables:
        return f"No tables found in library `{params.library}`. Check the library name with `wrds_list_libraries`."

    lines = [f"# Tables in `{params.library}` ({len(tables)})", ""]
    for t in tables:
        lines.append(f"- `{params.library}.{t}`")
    lines.append("")
    lines.append("Use `wrds_describe_table` to see column details.")
    return "\n".join(lines)


class DescribeTableInput(BaseModel):
    """Input for describing a WRDS table's columns."""
    model_config = ConfigDict(str_strip_whitespace=True)
    library: str = Field(..., description="WRDS library/schema name", min_length=1)
    table: str = Field(..., description="Table name within the library", min_length=1)

@mcp.tool(
    name="wrds_describe_table",
    annotations={
        "title": "Describe a WRDS Table",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def wrds_describe_table(params: DescribeTableInput, ctx: Context) -> str:
    """Describe columns, types, and row count of a WRDS table.

    Args:
        params: library (str) — schema; table (str) — table name

    Returns:
        Markdown table showing column name, data type, and nullable flag,
        plus approximate row count.
    """
    db = _get_db(ctx)

    # Column info
    col_sql = """
        SELECT column_name, data_type, is_nullable, character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = :schema AND table_name = :table
        ORDER BY ordinal_position
    """
    cols = await db.execute(col_sql, {"schema": params.library.lower(), "table": params.table.lower()})

    if cols.empty:
        return (
            f"Table `{params.library}.{params.table}` not found. "
            f"Use `wrds_list_tables` to see available tables."
        )

    # Approximate row count (fast)
    count_sql = f"""
        SELECT reltuples::bigint AS approx_rows
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = :schema AND c.relname = :table
    """
    try:
        count_df = await db.execute(count_sql, {"schema": params.library.lower(), "table": params.table.lower()})
        approx_rows = int(count_df.iloc[0]["approx_rows"]) if not count_df.empty else "unknown"
    except Exception:
        approx_rows = "unknown"

    lines = [
        f"# `{params.library}.{params.table}`",
        f"Approximate rows: **{approx_rows:,}**" if isinstance(approx_rows, int) else f"Approximate rows: {approx_rows}",
        "",
        "| Column | Type | Nullable |",
        "|--------|------|----------|"
    ]
    for _, row in cols.iterrows():
        dtype = row["data_type"]
        if row["character_maximum_length"]:
            dtype += f"({int(row['character_maximum_length'])})"
        nullable = "Yes" if row["is_nullable"] == "YES" else "No"
        lines.append(f"| `{row['column_name']}` | {dtype} | {nullable} |")

    return "\n".join(lines)


# ============================================================================
# CORE TOOLS — Query & Download
# ============================================================================

class RunSQLInput(BaseModel):
    """Input for executing a raw SQL query against WRDS."""
    model_config = ConfigDict(str_strip_whitespace=True)
    sql: str = Field(
        ..., description="SQL query to execute. Use schema-qualified table names (e.g., comp.funda).",
        min_length=5
    )
    max_rows: Optional[int] = Field(
        default=MAX_ROWS_DEFAULT,
        description="Maximum rows to return (default 1000, max 100000)",
        ge=1, le=MAX_ROWS_LIMIT
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="'markdown' for readable table, 'json' for raw data"
    )

    @field_validator("sql")
    @classmethod
    def validate_sql_readonly(cls, v: str) -> str:
        """Ensure the query is read-only."""
        dangerous = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE", "GRANT", "REVOKE"]
        first_word = v.strip().split()[0].upper()
        if first_word in dangerous:
            raise ValueError(f"Only SELECT queries are allowed. Got: {first_word}")
        return v

@mcp.tool(
    name="wrds_run_sql",
    annotations={
        "title": "Run SQL Query on WRDS",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def wrds_run_sql(params: RunSQLInput, ctx: Context) -> str:
    """Execute a read-only SQL query against WRDS and return results.

    Supports any SELECT query using schema-qualified table names.
    Results are limited to max_rows. For large downloads, use wrds_download_data.

    Args:
        params: sql (str), max_rows (int), response_format ('markdown'|'json')

    Returns:
        Query results as a markdown table or JSON string.
    """
    db = _get_db(ctx)

    # Add LIMIT if not present
    sql = params.sql.rstrip().rstrip(";")
    if "LIMIT" not in sql.upper():
        sql += f" LIMIT {params.max_rows}"

    try:
        df = await db.execute(sql)
    except Exception as e:
        return f"Error executing query: {e}"

    if df.empty:
        return "Query returned no results."

    if params.response_format == ResponseFormat.JSON:
        return df.to_json(orient="records", date_format="iso", indent=2)

    # Markdown table
    truncated = len(df) >= params.max_rows
    lines = [f"**{len(df)} rows returned**" + (" *(truncated)*" if truncated else ""), ""]
    lines.append(df.to_markdown(index=False))
    return "\n".join(lines)


class DownloadDataInput(BaseModel):
    """Input for downloading WRDS data to a file."""
    model_config = ConfigDict(str_strip_whitespace=True)
    sql: str = Field(
        ..., description="SQL SELECT query for the data to download",
        min_length=5
    )
    filename: str = Field(
        ..., description="Output filename (without extension, e.g., 'crsp_monthly_2020_2023')",
        min_length=1, max_length=200
    )
    format: ExportFormat = Field(
        default=ExportFormat.PARQUET,
        description="Export format: 'csv', 'parquet', or 'json'"
    )
    max_rows: Optional[int] = Field(
        default=MAX_ROWS_LIMIT,
        description="Maximum rows to download (default 100000)",
        ge=1, le=1_000_000
    )

    @field_validator("sql")
    @classmethod
    def validate_sql_readonly(cls, v: str) -> str:
        first_word = v.strip().split()[0].upper()
        dangerous = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE"]
        if first_word in dangerous:
            raise ValueError(f"Only SELECT queries are allowed. Got: {first_word}")
        return v

@mcp.tool(
    name="wrds_download_data",
    annotations={
        "title": "Download WRDS Data to File",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def wrds_download_data(params: DownloadDataInput, ctx: Context) -> str:
    """Download WRDS query results to a local file (CSV, Parquet, or JSON).

    Executes the SQL query and saves the resulting DataFrame. Files are saved
    to the WRDS_DOWNLOAD_DIR (default: ~/wrds_data/).

    Args:
        params: sql, filename, format ('csv'|'parquet'|'json'), max_rows

    Returns:
        Confirmation with file path, row count, and file size.
    """
    db = _get_db(ctx)
    download_dir = _get_download_dir(ctx)

    sql = params.sql.rstrip().rstrip(";")
    if "LIMIT" not in sql.upper():
        sql += f" LIMIT {params.max_rows}"

    try:
        df = await db.execute(sql)
    except Exception as e:
        return f"Error executing query: {e}"

    if df.empty:
        return "Query returned no results. No file created."

    # Determine file path
    ext = params.format.value
    filepath = os.path.join(download_dir, f"{params.filename}.{ext}")

    if params.format == ExportFormat.CSV:
        df.to_csv(filepath, index=False)
    elif params.format == ExportFormat.PARQUET:
        df.to_parquet(filepath, index=False, engine="pyarrow")
    elif params.format == ExportFormat.JSON:
        df.to_json(filepath, orient="records", date_format="iso", indent=2)

    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    return (
        f"Downloaded **{len(df):,} rows** to:\n\n"
        f"`{filepath}`\n\n"
        f"Format: {params.format.value.upper()} | Size: {size_mb:.2f} MB"
    )


# ============================================================================
# SMART TOOLS — Common Research Workflows
# ============================================================================

class CRSPReturnsInput(BaseModel):
    """Input for fetching CRSP stock returns."""
    model_config = ConfigDict(str_strip_whitespace=True)
    tickers: Optional[List[str]] = Field(
        default=None,
        description="List of stock tickers (e.g., ['AAPL', 'MSFT']). Omit for all stocks.",
        max_length=50
    )
    permnos: Optional[List[int]] = Field(
        default=None,
        description="List of CRSP PERMNOs. Alternative to tickers."
    )
    start_date: str = Field(
        ..., description="Start date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    end_date: str = Field(
        ..., description="End date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    frequency: str = Field(
        default="monthly",
        description="'daily' or 'monthly'"
    )
    max_rows: Optional[int] = Field(default=MAX_ROWS_DEFAULT, ge=1, le=MAX_ROWS_LIMIT)

@mcp.tool(
    name="wrds_get_crsp_returns",
    annotations={
        "title": "Get CRSP Stock Returns",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def wrds_get_crsp_returns(params: CRSPReturnsInput, ctx: Context) -> str:
    """Fetch CRSP stock returns for given tickers/PERMNOs and date range.

    Queries CRSP monthly (msf/msenames) or daily (dsf/dsenames) stock files.
    Returns key fields: permno, date, ticker, company name, return, price,
    shares outstanding, and volume.

    Args:
        params: tickers or permnos, start_date, end_date, frequency, max_rows

    Returns:
        Markdown table of returns data.
    """
    db = _get_db(ctx)

    if params.frequency == "daily":
        data_table = "crsp.dsf"
        names_table = "crsp.dsenames"
        date_col = "date"
    else:
        data_table = "crsp.msf"
        names_table = "crsp.msenames"
        date_col = "date"

    sql = f"""
        SELECT a.permno, a.{date_col} AS date, b.ticker, b.comnam AS company_name,
               a.ret, a.prc, a.shrout, a.vol
        FROM {data_table} a
        INNER JOIN {names_table} b
            ON a.permno = b.permno
            AND a.{date_col} BETWEEN b.namedt AND b.nameendt
        WHERE a.{date_col} BETWEEN :start_date AND :end_date
    """

    params_dict = {"start_date": params.start_date, "end_date": params.end_date}

    if params.tickers:
        placeholders = ", ".join([f":t{i}" for i in range(len(params.tickers))])
        sql += f" AND UPPER(b.ticker) IN ({placeholders})"
        for i, t in enumerate(params.tickers):
            params_dict[f"t{i}"] = t.upper()
    elif params.permnos:
        placeholders = ", ".join([f":p{i}" for i in range(len(params.permnos))])
        sql += f" AND a.permno IN ({placeholders})"
        for i, p in enumerate(params.permnos):
            params_dict[f"p{i}"] = p

    sql += f" ORDER BY a.permno, a.{date_col} LIMIT {params.max_rows}"

    try:
        df = await db.execute(sql, params_dict)
    except Exception as e:
        return f"Error: {e}"

    if df.empty:
        return "No CRSP returns found for the given parameters."

    lines = [f"**CRSP {params.frequency} returns: {len(df):,} rows**", ""]
    lines.append(df.head(50).to_markdown(index=False))
    if len(df) > 50:
        lines.append(f"\n*Showing first 50 of {len(df):,} rows. Use `wrds_download_data` for the full dataset.*")
    return "\n".join(lines)


class CompustatFundamentalsInput(BaseModel):
    """Input for fetching Compustat financial statement data."""
    model_config = ConfigDict(str_strip_whitespace=True)
    tickers: Optional[List[str]] = Field(default=None, description="Stock tickers", max_length=50)
    gvkeys: Optional[List[str]] = Field(default=None, description="Compustat GVKEYs")
    start_year: int = Field(..., description="Start fiscal year", ge=1950, le=2030)
    end_year: int = Field(..., description="End fiscal year", ge=1950, le=2030)
    frequency: str = Field(default="annual", description="'annual' (funda) or 'quarterly' (fundq)")
    variables: Optional[List[str]] = Field(
        default=None,
        description="Specific Compustat variables to retrieve (e.g., ['at', 'lt', 'sale', 'ni']). If omitted, returns common variables."
    )
    max_rows: Optional[int] = Field(default=MAX_ROWS_DEFAULT, ge=1, le=MAX_ROWS_LIMIT)

@mcp.tool(
    name="wrds_get_compustat",
    annotations={
        "title": "Get Compustat Financial Data",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def wrds_get_compustat(params: CompustatFundamentalsInput, ctx: Context) -> str:
    """Fetch Compustat annual or quarterly financial statement data.

    Retrieves from comp.funda (annual) or comp.fundq (quarterly).
    Default variables include: gvkey, datadate, tic, conm, fyear, at, lt,
    sale, revt, ni, ceq, csho, prcc_f.

    Args:
        params: tickers or gvkeys, start_year, end_year, frequency, variables, max_rows

    Returns:
        Markdown table of financial data.
    """
    db = _get_db(ctx)

    table = "comp.funda" if params.frequency == "annual" else "comp.fundq"
    year_col = "fyear" if params.frequency == "annual" else "fyearq"

    default_vars = ["gvkey", "datadate", "tic", "conm", year_col,
                    "at", "lt", "sale", "revt", "ni", "ceq", "csho", "prcc_f"]
    if params.variables:
        # Always include identifiers
        select_vars = list(set(["gvkey", "datadate", "tic", "conm", year_col] + params.variables))
    else:
        select_vars = default_vars

    select_clause = ", ".join(select_vars)
    sql = f"""
        SELECT {select_clause}
        FROM {table}
        WHERE datafmt = 'STD' AND indfmt = 'INDL' AND consol = 'C' AND popsrc = 'D'
          AND {year_col} BETWEEN :start_year AND :end_year
    """
    params_dict = {"start_year": params.start_year, "end_year": params.end_year}

    if params.tickers:
        placeholders = ", ".join([f":t{i}" for i in range(len(params.tickers))])
        sql += f" AND UPPER(tic) IN ({placeholders})"
        for i, t in enumerate(params.tickers):
            params_dict[f"t{i}"] = t.upper()
    elif params.gvkeys:
        placeholders = ", ".join([f":g{i}" for i in range(len(params.gvkeys))])
        sql += f" AND gvkey IN ({placeholders})"
        for i, g in enumerate(params.gvkeys):
            params_dict[f"g{i}"] = g

    sql += f" ORDER BY gvkey, datadate LIMIT {params.max_rows}"

    try:
        df = await db.execute(sql, params_dict)
    except Exception as e:
        return f"Error: {e}"

    if df.empty:
        return "No Compustat data found for the given parameters."

    lines = [f"**Compustat {params.frequency} data: {len(df):,} rows**", ""]
    lines.append(df.head(50).to_markdown(index=False))
    if len(df) > 50:
        lines.append(f"\n*Showing first 50 of {len(df):,} rows.*")
    return "\n".join(lines)


class CCMMergeInput(BaseModel):
    """Input for merging CRSP and Compustat via the CCM link table."""
    model_config = ConfigDict(str_strip_whitespace=True)
    start_date: str = Field(..., description="Start date YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: str = Field(..., description="End date YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$")
    tickers: Optional[List[str]] = Field(default=None, description="Filter by tickers", max_length=50)
    compustat_vars: Optional[List[str]] = Field(
        default=None,
        description="Compustat variables to include (e.g., ['at', 'lt', 'ni'])"
    )
    crsp_vars: Optional[List[str]] = Field(
        default=None,
        description="CRSP variables to include (e.g., ['ret', 'prc', 'shrout'])"
    )
    max_rows: Optional[int] = Field(default=MAX_ROWS_DEFAULT, ge=1, le=MAX_ROWS_LIMIT)

@mcp.tool(
    name="wrds_merge_crsp_compustat",
    annotations={
        "title": "Merge CRSP and Compustat (CCM)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def wrds_merge_crsp_compustat(params: CCMMergeInput, ctx: Context) -> str:
    """Merge CRSP monthly returns with Compustat annual fundamentals via CCM link table.

    Uses crsp.ccmxpf_lnkhist to link CRSP PERMNO to Compustat GVKEY.
    Returns merged dataset with both market data and accounting fundamentals.

    Args:
        params: start_date, end_date, tickers, compustat_vars, crsp_vars, max_rows

    Returns:
        Markdown table of merged CRSP-Compustat data.
    """
    db = _get_db(ctx)

    comp_vars = params.compustat_vars or ["at", "lt", "sale", "ni", "ceq"]
    crsp_vars_list = params.crsp_vars or ["ret", "prc", "shrout", "vol"]

    comp_select = ", ".join([f"c.{v}" for v in comp_vars])
    crsp_select = ", ".join([f"m.{v}" for v in crsp_vars_list])

    sql = f"""
        SELECT c.gvkey, c.datadate, c.tic, c.conm, c.fyear,
               {comp_select},
               l.lpermno AS permno,
               m.date AS crsp_date,
               {crsp_select}
        FROM comp.funda c
        INNER JOIN crsp.ccmxpf_lnkhist l
            ON c.gvkey = l.gvkey
            AND l.linktype IN ('LU', 'LC')
            AND l.linkprim IN ('P', 'C')
            AND c.datadate >= l.linkdt
            AND (c.datadate <= l.linkenddt OR l.linkenddt IS NULL)
        INNER JOIN crsp.msf m
            ON l.lpermno = m.permno
            AND m.date BETWEEN c.datadate AND (c.datadate + INTERVAL '3 months')
        WHERE c.datafmt = 'STD' AND c.indfmt = 'INDL' AND c.consol = 'C' AND c.popsrc = 'D'
          AND c.datadate BETWEEN :start_date AND :end_date
    """
    params_dict = {"start_date": params.start_date, "end_date": params.end_date}

    if params.tickers:
        placeholders = ", ".join([f":t{i}" for i in range(len(params.tickers))])
        sql += f" AND UPPER(c.tic) IN ({placeholders})"
        for i, t in enumerate(params.tickers):
            params_dict[f"t{i}"] = t.upper()

    sql += f" ORDER BY c.gvkey, c.datadate LIMIT {params.max_rows}"

    try:
        df = await db.execute(sql, params_dict)
    except Exception as e:
        return f"Error: {e}"

    if df.empty:
        return "No merged CRSP-Compustat data found."

    lines = [f"**CRSP-Compustat Merged: {len(df):,} rows**", ""]
    lines.append(df.head(50).to_markdown(index=False))
    if len(df) > 50:
        lines.append(f"\n*Showing first 50 of {len(df):,} rows.*")
    return "\n".join(lines)


class SampleDataInput(BaseModel):
    """Input for previewing a WRDS table."""
    model_config = ConfigDict(str_strip_whitespace=True)
    library: str = Field(..., description="WRDS library/schema name", min_length=1)
    table: str = Field(..., description="Table name", min_length=1)
    rows: Optional[int] = Field(default=10, description="Number of sample rows", ge=1, le=100)

@mcp.tool(
    name="wrds_sample_data",
    annotations={
        "title": "Preview Sample Rows from a WRDS Table",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def wrds_sample_data(params: SampleDataInput, ctx: Context) -> str:
    """Fetch a small sample of rows from any WRDS table for quick inspection.

    Useful for understanding data structure and content before writing queries.

    Args:
        params: library, table, rows (default 10)

    Returns:
        Markdown table of sample rows.
    """
    db = _get_db(ctx)
    sql = f"SELECT * FROM {params.library}.{params.table} LIMIT {params.rows}"

    try:
        df = await db.execute(sql)
    except Exception as e:
        return f"Error: {e}"

    if df.empty:
        return f"Table `{params.library}.{params.table}` appears empty."

    lines = [f"**Sample from `{params.library}.{params.table}` ({len(df)} rows)**", ""]
    lines.append(df.to_markdown(index=False))
    return "\n".join(lines)


# ============================================================================
# SMART TOOLS — IBES Analyst Estimates
# ============================================================================

class IBESEstimatesInput(BaseModel):
    """Input for fetching IBES analyst earnings estimates."""
    model_config = ConfigDict(str_strip_whitespace=True)
    tickers: Optional[List[str]] = Field(
        default=None, description="IBES ticker symbols (e.g., ['AAPL', 'MSFT'])", max_length=50
    )
    start_date: str = Field(..., description="Start date YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: str = Field(..., description="End date YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$")
    data_type: str = Field(
        default="summary",
        description="'summary' for consensus stats, 'detail' for individual analyst estimates, 'actuals' for actual EPS"
    )
    max_rows: Optional[int] = Field(default=MAX_ROWS_DEFAULT, ge=1, le=MAX_ROWS_LIMIT)

@mcp.tool(
    name="wrds_get_ibes_estimates",
    annotations={
        "title": "Get IBES Analyst Estimates",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def wrds_get_ibes_estimates(params: IBESEstimatesInput, ctx: Context) -> str:
    """Fetch IBES analyst earnings estimates — consensus summary, individual detail, or actuals.

    Queries:
    - summary: ibes.statsumu_epsus (mean, median, stdev of EPS forecasts)
    - detail: ibes.detu_epsus (individual analyst EPS estimates)
    - actuals: ibes.actu_epsus (reported actual EPS)

    Args:
        params: tickers, start_date, end_date, data_type, max_rows

    Returns:
        Markdown table of IBES data.
    """
    db = _get_db(ctx)

    if params.data_type == "detail":
        sql = """
            SELECT ticker, cusip, analys, estimator, fpedats, revdats, revtims,
                   value, fpi
            FROM ibes.detu_epsus
            WHERE fpedats BETWEEN :start_date AND :end_date
        """
    elif params.data_type == "actuals":
        sql = """
            SELECT ticker, cusip, pends, pdicity, measure, value, anndats
            FROM ibes.actu_epsus
            WHERE pends BETWEEN :start_date AND :end_date
        """
    else:  # summary
        sql = """
            SELECT ticker, cusip, fpedats, statpers, meanest, medest, stdev,
                   numest, highest, lowest, fpi
            FROM ibes.statsumu_epsus
            WHERE statpers BETWEEN :start_date AND :end_date
        """

    params_dict = {"start_date": params.start_date, "end_date": params.end_date}

    if params.tickers:
        placeholders = ", ".join([f":t{i}" for i in range(len(params.tickers))])
        sql += f" AND UPPER(ticker) IN ({placeholders})"
        for i, t in enumerate(params.tickers):
            params_dict[f"t{i}"] = t.upper()

    sql += f" LIMIT {params.max_rows}"

    try:
        df = await db.execute(sql, params_dict)
    except Exception as e:
        return f"Error: {e}"

    if df.empty:
        return "No IBES data found for the given parameters."

    lines = [f"**IBES {params.data_type} estimates: {len(df):,} rows**", ""]
    lines.append(df.head(50).to_markdown(index=False))
    if len(df) > 50:
        lines.append(f"\n*Showing first 50 of {len(df):,} rows.*")
    return "\n".join(lines)


# ============================================================================
# SMART TOOLS — Fama-French Factors
# ============================================================================

class FamaFrenchInput(BaseModel):
    """Input for fetching Fama-French factor data."""
    model_config = ConfigDict(str_strip_whitespace=True)
    model: str = Field(
        default="ff3",
        description="Factor model: 'ff3' (3-factor), 'ff5' (5-factor), 'momentum'"
    )
    frequency: str = Field(default="monthly", description="'daily' or 'monthly'")
    start_date: str = Field(..., description="Start date YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: str = Field(..., description="End date YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$")

@mcp.tool(
    name="wrds_get_fama_french",
    annotations={
        "title": "Get Fama-French Factor Returns",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def wrds_get_fama_french(params: FamaFrenchInput, ctx: Context) -> str:
    """Fetch Fama-French factor returns from the Ken French data library on WRDS.

    Available models:
    - ff3: Market excess return (mktrf), SMB, HML, RF
    - ff5: FF3 + RMW (profitability), CMA (investment)
    - momentum: UMD (up minus down) momentum factor

    Args:
        params: model ('ff3'|'ff5'|'momentum'), frequency, start_date, end_date

    Returns:
        Markdown table of factor returns.
    """
    db = _get_db(ctx)

    # Fama-French tables on WRDS vary by institution; try common schemas
    if params.frequency == "monthly":
        if params.model == "ff5":
            table = "ff.fivefactors_monthly"
        elif params.model == "momentum":
            table = "ff.momentum_monthly"
        else:
            table = "ff.factors_monthly"
    else:
        if params.model == "ff5":
            table = "ff.fivefactors_daily"
        elif params.model == "momentum":
            table = "ff.momentum_daily"
        else:
            table = "ff.factors_daily"

    sql = f"""
        SELECT *
        FROM {table}
        WHERE date BETWEEN :start_date AND :end_date
        ORDER BY date
    """
    params_dict = {"start_date": params.start_date, "end_date": params.end_date}

    try:
        df = await db.execute(sql, params_dict)
    except Exception as e:
        # Try alternative schema name
        alt_table = table.replace("ff.", "ff_all.")
        try:
            sql_alt = sql.replace(table, alt_table)
            df = await db.execute(sql_alt, params_dict)
        except Exception as e2:
            return (
                f"Error querying Fama-French factors. Tried `{table}` and `{alt_table}`. "
                f"Use `wrds_list_libraries` with filter='ff' to find the correct schema. "
                f"Detail: {e2}"
            )

    if df.empty:
        return "No Fama-French data found for the given date range."

    lines = [f"**Fama-French {params.model.upper()} {params.frequency} factors: {len(df):,} rows**", ""]
    lines.append(df.to_markdown(index=False))
    return "\n".join(lines)


# ============================================================================
# SMART TOOLS — Institutional Holdings (13F)
# ============================================================================

class Holdings13FInput(BaseModel):
    """Input for fetching institutional holdings from Thomson Reuters 13F."""
    model_config = ConfigDict(str_strip_whitespace=True)
    cusips: Optional[List[str]] = Field(
        default=None, description="CUSIPs to filter by (security level)", max_length=50
    )
    manager_name: Optional[str] = Field(
        default=None, description="Manager/fund name to search for (partial match)"
    )
    start_date: str = Field(..., description="Start date YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: str = Field(..., description="End date YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$")
    max_rows: Optional[int] = Field(default=MAX_ROWS_DEFAULT, ge=1, le=MAX_ROWS_LIMIT)

@mcp.tool(
    name="wrds_get_13f_holdings",
    annotations={
        "title": "Get Institutional Holdings (13F)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def wrds_get_13f_holdings(params: Holdings13FInput, ctx: Context) -> str:
    """Fetch institutional holdings from Thomson Reuters 13F filings.

    Queries tfn.s34 (S34 master file) for institutional ownership data.
    Shows manager, security, shares held, and market value by quarter.

    Args:
        params: cusips, manager_name, start_date, end_date, max_rows

    Returns:
        Markdown table of institutional holdings.
    """
    db = _get_db(ctx)

    sql = """
        SELECT s.mgrno, s.mgrname, s.rdate, s.cusip,
               s.shares, s.prc AS price, s.shrout1 AS shares_outstanding,
               s.sole, s.shared, s.no AS no_voting
        FROM tfn.s34 s
        WHERE s.rdate BETWEEN :start_date AND :end_date
    """
    params_dict = {"start_date": params.start_date, "end_date": params.end_date}

    if params.cusips:
        placeholders = ", ".join([f":c{i}" for i in range(len(params.cusips))])
        sql += f" AND s.cusip IN ({placeholders})"
        for i, c in enumerate(params.cusips):
            params_dict[f"c{i}"] = c

    if params.manager_name:
        sql += " AND UPPER(s.mgrname) LIKE :mgr_name"
        params_dict["mgr_name"] = f"%{params.manager_name.upper()}%"

    sql += f" ORDER BY s.rdate, s.mgrno LIMIT {params.max_rows}"

    try:
        df = await db.execute(sql, params_dict)
    except Exception as e:
        return f"Error: {e}. Try `wrds_list_tables` with library='tfn' to verify table names."

    if df.empty:
        return "No 13F holdings found for the given parameters."

    lines = [f"**13F Institutional Holdings: {len(df):,} rows**", ""]
    lines.append(df.head(50).to_markdown(index=False))
    if len(df) > 50:
        lines.append(f"\n*Showing first 50 of {len(df):,} rows.*")
    return "\n".join(lines)


# ============================================================================
# SMART TOOLS — Audit Analytics
# ============================================================================

class AuditAnalyticsInput(BaseModel):
    """Input for fetching Audit Analytics data."""
    model_config = ConfigDict(str_strip_whitespace=True)
    data_type: str = Field(
        default="fees",
        description="'fees' (audit fees), 'opinions' (audit opinions), 'restatements', 'sox404' (internal controls)"
    )
    start_year: int = Field(..., description="Start fiscal year", ge=2000, le=2030)
    end_year: int = Field(..., description="End fiscal year", ge=2000, le=2030)
    company_ciks: Optional[List[str]] = Field(
        default=None, description="CIK numbers to filter by"
    )
    max_rows: Optional[int] = Field(default=MAX_ROWS_DEFAULT, ge=1, le=MAX_ROWS_LIMIT)

@mcp.tool(
    name="wrds_get_audit_analytics",
    annotations={
        "title": "Get Audit Analytics Data",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def wrds_get_audit_analytics(params: AuditAnalyticsInput, ctx: Context) -> str:
    """Fetch Audit Analytics data — fees, opinions, restatements, or SOX 404.

    Tables queried:
    - fees: audit.feed03_audit_fees
    - opinions: audit.feed05_audit_opinions
    - restatements: audit.feed09_nonreliance_restatements
    - sox404: audit.feed11_sox_404_internal_controls

    Args:
        params: data_type, start_year, end_year, company_ciks, max_rows

    Returns:
        Markdown table of audit data.
    """
    db = _get_db(ctx)

    table_map = {
        "fees": "audit.feed03_audit_fees",
        "opinions": "audit.feed05_audit_opinions",
        "restatements": "audit.feed09_nonreliance_restatements",
        "sox404": "audit.feed11_sox_404_internal_controls",
    }
    table = table_map.get(params.data_type)
    if not table:
        return f"Invalid data_type '{params.data_type}'. Options: fees, opinions, restatements, sox404"

    sql = f"SELECT * FROM {table} WHERE fiscal_year BETWEEN :start_year AND :end_year"
    params_dict = {"start_year": params.start_year, "end_year": params.end_year}

    if params.company_ciks:
        placeholders = ", ".join([f":cik{i}" for i in range(len(params.company_ciks))])
        sql += f" AND company_fkey IN ({placeholders})"
        for i, cik in enumerate(params.company_ciks):
            params_dict[f"cik{i}"] = cik

    sql += f" LIMIT {params.max_rows}"

    try:
        df = await db.execute(sql, params_dict)
    except Exception as e:
        return (
            f"Error querying {table}: {e}. "
            f"Column names vary across Audit Analytics tables. "
            f"Use `wrds_describe_table` to check the exact schema."
        )

    if df.empty:
        return f"No Audit Analytics {params.data_type} data found."

    lines = [f"**Audit Analytics ({params.data_type}): {len(df):,} rows**", ""]
    lines.append(df.head(50).to_markdown(index=False))
    if len(df) > 50:
        lines.append(f"\n*Showing first 50 of {len(df):,} rows.*")
    return "\n".join(lines)


# ============================================================================
# SMART TOOLS — ExecuComp
# ============================================================================

class ExecuCompInput(BaseModel):
    """Input for fetching executive compensation data."""
    model_config = ConfigDict(str_strip_whitespace=True)
    tickers: Optional[List[str]] = Field(default=None, description="Stock tickers", max_length=50)
    gvkeys: Optional[List[str]] = Field(default=None, description="Compustat GVKEYs")
    start_year: int = Field(..., description="Start year", ge=1992, le=2030)
    end_year: int = Field(..., description="End year", ge=1992, le=2030)
    exec_title: Optional[str] = Field(
        default=None, description="Filter by executive title (e.g., 'CEO', 'CFO')"
    )
    variables: Optional[List[str]] = Field(
        default=None,
        description="Specific compensation variables (e.g., ['salary', 'bonus', 'tdc1', 'option_awards_blk_value'])"
    )
    max_rows: Optional[int] = Field(default=MAX_ROWS_DEFAULT, ge=1, le=MAX_ROWS_LIMIT)

@mcp.tool(
    name="wrds_get_execucomp",
    annotations={
        "title": "Get ExecuComp Executive Compensation",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def wrds_get_execucomp(params: ExecuCompInput, ctx: Context) -> str:
    """Fetch executive compensation data from ExecuComp.

    Queries execcomp.anncomp for annual executive pay including salary, bonus,
    stock awards, option awards, and total compensation.

    Default variables: gvkey, year, execid, exec_fullname, titleann, salary,
    bonus, stock_awards, option_awards_blk_value, noneq_incent, tdc1, tdc2.

    Args:
        params: tickers, gvkeys, start_year, end_year, exec_title, variables, max_rows

    Returns:
        Markdown table of compensation data.
    """
    db = _get_db(ctx)

    default_vars = [
        "gvkey", "year", "execid", "exec_fullname", "titleann",
        "salary", "bonus", "stock_awards", "option_awards_blk_value",
        "noneq_incent", "tdc1", "tdc2", "ticker"
    ]
    if params.variables:
        select_vars = list(set(["gvkey", "year", "execid", "exec_fullname", "titleann", "ticker"] + params.variables))
    else:
        select_vars = default_vars

    select_clause = ", ".join(select_vars)
    sql = f"""
        SELECT {select_clause}
        FROM execcomp.anncomp
        WHERE year BETWEEN :start_year AND :end_year
    """
    params_dict = {"start_year": params.start_year, "end_year": params.end_year}

    if params.tickers:
        placeholders = ", ".join([f":t{i}" for i in range(len(params.tickers))])
        sql += f" AND UPPER(ticker) IN ({placeholders})"
        for i, t in enumerate(params.tickers):
            params_dict[f"t{i}"] = t.upper()
    elif params.gvkeys:
        placeholders = ", ".join([f":g{i}" for i in range(len(params.gvkeys))])
        sql += f" AND gvkey IN ({placeholders})"
        for i, g in enumerate(params.gvkeys):
            params_dict[f"g{i}"] = g

    if params.exec_title:
        sql += " AND UPPER(titleann) LIKE :title"
        params_dict["title"] = f"%{params.exec_title.upper()}%"

    sql += f" ORDER BY gvkey, year, execid LIMIT {params.max_rows}"

    try:
        df = await db.execute(sql, params_dict)
    except Exception as e:
        return f"Error: {e}. Use `wrds_describe_table` with library='execcomp', table='anncomp' to check columns."

    if df.empty:
        return "No ExecuComp data found for the given parameters."

    lines = [f"**ExecuComp Compensation: {len(df):,} rows**", ""]
    lines.append(df.head(50).to_markdown(index=False))
    if len(df) > 50:
        lines.append(f"\n*Showing first 50 of {len(df):,} rows.*")
    return "\n".join(lines)


# ============================================================================
# SMART TOOLS — PitchBook (VC/PE)
# ============================================================================

class PitchBookInput(BaseModel):
    """Input for fetching PitchBook deal data."""
    model_config = ConfigDict(str_strip_whitespace=True)
    data_type: str = Field(
        default="deals",
        description="'deals' (transactions), 'companies' (company profiles), 'funds' (fund data)"
    )
    start_date: Optional[str] = Field(
        default=None, description="Start date YYYY-MM-DD (for deals)", pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    end_date: Optional[str] = Field(
        default=None, description="End date YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    search_term: Optional[str] = Field(
        default=None, description="Search company or fund name (partial match)"
    )
    max_rows: Optional[int] = Field(default=MAX_ROWS_DEFAULT, ge=1, le=MAX_ROWS_LIMIT)

@mcp.tool(
    name="wrds_get_pitchbook",
    annotations={
        "title": "Get PitchBook VC/PE Data",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def wrds_get_pitchbook(params: PitchBookInput, ctx: Context) -> str:
    """Fetch PitchBook venture capital and private equity data.

    Queries the pitchbook schema for deal transactions, company profiles,
    or fund information. PitchBook covers 1.6M+ deals, 3M+ companies, 31K funds.

    Note: PitchBook table names may vary. If this tool fails, use wrds_list_tables
    with library='pitchbook' to discover the exact table names available.

    Args:
        params: data_type ('deals'|'companies'|'funds'), date range, search_term, max_rows

    Returns:
        Markdown table of PitchBook data.
    """
    db = _get_db(ctx)

    # PitchBook schema on WRDS is 'pitchbk'
    if params.data_type == "companies":
        sql = "SELECT * FROM pitchbk.company WHERE 1=1"
    elif params.data_type == "funds":
        sql = "SELECT * FROM pitchbk.fund WHERE 1=1"
    else:
        sql = "SELECT * FROM pitchbk.deal WHERE 1=1"

    params_dict = {}

    if params.start_date and params.end_date:
        sql += " AND announceddate BETWEEN :start_date AND :end_date"
        params_dict["start_date"] = params.start_date
        params_dict["end_date"] = params.end_date

    if params.search_term:
        sql += " AND UPPER(companyname) LIKE :search"
        params_dict["search"] = f"%{params.search_term.upper()}%"

    sql += f" LIMIT {params.max_rows}"

    try:
        df = await db.execute(sql, params_dict)
    except Exception as e:
        return (
            f"Error querying PitchBook: {e}\n\n"
            f"PitchBook table/column names vary by WRDS subscription. "
            f"Use `wrds_list_tables` with library='pitchbk' and `wrds_describe_table` "
            f"to discover the exact schema available to you."
        )

    if df.empty:
        return "No PitchBook data found."

    lines = [f"**PitchBook {params.data_type}: {len(df):,} rows**", ""]
    lines.append(df.head(50).to_markdown(index=False))
    if len(df) > 50:
        lines.append(f"\n*Showing first 50 of {len(df):,} rows.*")
    return "\n".join(lines)


# ============================================================================
# SMART TOOLS — Revelio Labs (Workforce Data)
# ============================================================================

class RevelioInput(BaseModel):
    """Input for fetching Revelio Labs workforce data."""
    model_config = ConfigDict(str_strip_whitespace=True)
    data_type: str = Field(
        default="positions",
        description="'positions' (work history), 'postings' (job postings), 'sentiment' (employee reviews)"
    )
    company_name: Optional[str] = Field(
        default=None, description="Company name to search for (partial match)"
    )
    start_date: Optional[str] = Field(
        default=None, description="Start date YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    end_date: Optional[str] = Field(
        default=None, description="End date YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    max_rows: Optional[int] = Field(default=MAX_ROWS_DEFAULT, ge=1, le=MAX_ROWS_LIMIT)

@mcp.tool(
    name="wrds_get_revelio",
    annotations={
        "title": "Get Revelio Labs Workforce Data",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def wrds_get_revelio(params: RevelioInput, ctx: Context) -> str:
    """Fetch Revelio Labs workforce analytics data.

    Queries the revelio schema for professional positions (work history),
    job postings, or employee sentiment data. Covers global workforce data
    from 2008 onwards.

    Note: Revelio table names may vary. If this tool fails, use wrds_list_tables
    with library='revelio' to discover available tables.

    Args:
        params: data_type, company_name, date range, max_rows

    Returns:
        Markdown table of workforce data.
    """
    db = _get_db(ctx)

    table_map = {
        "positions": "revelio.individual_positions",
        "postings": "revelio.postings_cosmos",
        "sentiment": "revelio.sentiment_individual_reviews",
    }
    table = table_map.get(params.data_type, "revelio.individual_positions")

    sql = f"SELECT * FROM {table} WHERE 1=1"
    params_dict = {}

    if params.company_name:
        sql += " AND UPPER(company_name) LIKE :company"
        params_dict["company"] = f"%{params.company_name.upper()}%"

    if params.start_date and params.end_date:
        sql += " AND start_date >= :start_date AND start_date <= :end_date"
        params_dict["start_date"] = params.start_date
        params_dict["end_date"] = params.end_date

    sql += f" LIMIT {params.max_rows}"

    try:
        df = await db.execute(sql, params_dict)
    except Exception as e:
        return (
            f"Error querying Revelio: {e}\n\n"
            f"Revelio table/column names vary. Use `wrds_list_tables` with "
            f"library='revelio' and `wrds_describe_table` to discover the exact schema."
        )

    if df.empty:
        return "No Revelio data found."

    lines = [f"**Revelio {params.data_type}: {len(df):,} rows**", ""]
    lines.append(df.head(50).to_markdown(index=False))
    if len(df) > 50:
        lines.append(f"\n*Showing first 50 of {len(df):,} rows.*")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()
