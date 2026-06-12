> **Web guide:** [docs/wrds-mcp.html](../docs/wrds-mcp.html) (GitHub Pages: `https://barrios88.github.io/barrios-skills/wrds-mcp.html`)

# WRDS MCP setup (John Barrios)

The **wrds-mcp** server lets Cursor, Claude, and other MCP clients query WRDS (Compustat, CRSP, Form 4, etc.) using natural language. You need:

1. An active **WRDS account** (your own username and password from Wharton)
2. **Duo MFA** enrolled on your WRDS account
3. Python 3.10+

This repo bundles the MCP server in [`mcp/wrds-mcp/`](../mcp/wrds-mcp/) and a **persistent tunnel** so you approve Duo **once per work session**, not on every query.

---

## Step 1 — Install the MCP server

```bash
cd barrios-skills/mcp/wrds-mcp
python3 -m venv ~/.wrds-mcp-env
source ~/.wrds-mcp-env/bin/activate
pip install -e .
```

Verify:

```bash
which wrds-mcp
# should print ~/.wrds-mcp-env/bin/wrds-mcp
```

---

## Step 2 — Set **your** WRDS credentials

WRDS assigns each researcher a unique username (often `firstname_lastname` or `jsmith_yale`). Use **your** credentials — not anyone else's.

### Option A — Shell environment (recommended for tunnel scripts)

```bash
export WRDS_USERNAME="your_wrds_username"
export WRDS_PASSWORD="your_wrds_password"
```

Add to `~/.zshrc` only if you accept storing credentials in your shell profile, or use a private file:

```bash
cp mcp/wrds-mcp/.env.example ~/.wrds-mcp.env
# edit ~/.wrds-mcp.env with your username and password
chmod 600 ~/.wrds-mcp.env
source ~/.wrds-mcp.env
```

### Option B — MCP server registration only

Pass credentials in the MCP config `env` block (see Step 4). The MCP server reads `WRDS_USERNAME` and `WRDS_PASSWORD` from the environment — it never hardcodes them.

**Security:** Do not commit real passwords. Do not paste credentials into GitHub issues or shared chats.

---

## Step 3 — Start the persistent tunnel (once per session)

WRDS requires Duo MFA. The tunnel daemon opens **one** SSH session; you approve Duo on your phone once, then all MCP queries reuse the tunnel.

```bash
cd barrios-skills/mcp/wrds-mcp/tunnel
bash tunnel_up.sh
# Approve the Duo Push within ~30 seconds
# -> "tunnel up on 127.0.0.1:49600"
```

Check status:

```bash
export WRDS_USERNAME="your_wrds_username"
export WRDS_PASSWORD="your_wrds_password"
bash tunnel_status.sh
```

When finished for the day:

```bash
bash tunnel_down.sh
```

Tunnel state lives in `~/.wrds-tunnel/` (logs and PID). Override with `WRDS_TUNNEL_STATE_DIR` if needed.

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `WRDS_USERNAME` | **Yes** | — | Your WRDS login |
| `WRDS_PASSWORD` | **Yes** | — | Your WRDS password |
| `WRDS_LOCAL_PORT` | No | `49600` | Local port the daemon listens on |
| `WRDS_TUNNEL_PORT` | No | — | Tell the MCP to use this port (set in MCP config) |
| `WRDS_DUO_RESPONSE` | No | `push` | Duo response: `push`, `phone`, or passcode |
| `WRDS_PYBIN` | No | `python3` | Python with `paramiko` installed |

---

## Step 4 — Register the MCP server

### Claude Code

```bash
claude mcp add wrds-mcp ~/.wrds-mcp-env/bin/wrds-mcp \
  -s user \
  --env WRDS_USERNAME=your_wrds_username \
  --env WRDS_PASSWORD=your_wrds_password \
  --env WRDS_TUNNEL_PORT=49600
```

Replace `your_wrds_username` and `your_wrds_password` with **your** WRDS account. Inspect: `claude mcp get wrds-mcp`.

### Cursor

Edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "wrds-mcp": {
      "command": "/Users/YOUR_USER/.wrds-mcp-env/bin/wrds-mcp",
      "args": [],
      "env": {
        "WRDS_USERNAME": "your_wrds_username",
        "WRDS_PASSWORD": "your_wrds_password",
        "WRDS_TUNNEL_PORT": "49600"
      }
    }
  }
}
```

Use the full path to `wrds-mcp` in **your** home directory. Restart Cursor after saving.

### Codex / other MCP clients

Same pattern: stdio command `wrds-mcp`, env vars `WRDS_USERNAME`, `WRDS_PASSWORD`, and `WRDS_TUNNEL_PORT=49600`.

---

## Step 5 — Daily workflow

```bash
# Morning: credentials + tunnel
source ~/.wrds-mcp.env   # or export WRDS_USERNAME / WRDS_PASSWORD
bash mcp/wrds-mcp/tunnel/tunnel_up.sh    # approve Duo once

# Use your AI tool normally — ask for Compustat, CRSP, etc.
# The wrds skill (skills/econometrics/wrds/) guides query filters.

# Evening:
bash mcp/wrds-mcp/tunnel/tunnel_down.sh
```

**Order matters:** tunnel must be up **before** the first MCP query. If you see "nothing is listening on WRDS_TUNNEL_PORT", run `tunnel_up.sh` again.

---

## MCP tools available

| Tool | Use for |
|------|---------|
| `wrds_list_libraries` | Browse WRDS schemas |
| `wrds_list_tables` | Tables in a library |
| `wrds_describe_table` | Column names and types |
| `wrds_sample_data` | Preview rows |
| `wrds_run_sql` | Read-only SQL |
| `wrds_download_data` | Export CSV / Parquet / JSON |
| `wrds_get_crsp_returns` | CRSP returns helper |
| `wrds_get_compustat` | Compustat helper |
| `wrds_merge_crsp_compustat` | CCM merge helper |

Pair with the [`wrds` skill](../skills/econometrics/wrds/SKILL.md) for Compustat filters, CRSP share codes, and Form 4 conventions.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `WRDS_USERNAME and WRDS_PASSWORD must be exported` | Export both before `tunnel_up.sh` |
| `authentication failed` | Wrong username/password, or WRDS account inactive |
| Duo not approved in time | Re-run `tunnel_up.sh` and approve faster |
| `connection refused` on port 49600 | Run `tunnel_up.sh`; check `tunnel_status.sh` |
| Port already in use | `tunnel_down.sh`, then `tunnel_up.sh` |
| MCP works but queries return bad data | Use the wrds skill filter checklist (Compustat `indfmt`, CRSP share types, etc.) |

Logs: `~/.wrds-tunnel/daemon.log`

---

## Alternative: `~/.pgpass` (Python scripts only)

For direct `psycopg2` scripts (not the MCP tunnel flow), you can use PostgreSQL password file:

```
wrds-pgdata.wharton.upenn.edu:9737:wrds:YOUR_WRDS_USERNAME:YOUR_WRDS_PASSWORD
```

```bash
chmod 600 ~/.pgpass
```

The MCP + tunnel workflow above is recommended for AI agents because it handles Duo MFA cleanly.
