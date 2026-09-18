#!/usr/bin/env bash
# tunnel_up.sh -- launch the paramiko tunnel daemon in the background.
#
# Why paramiko: WRDS-cloud bastion has password auth disabled. Only keyboard-
# interactive (Duo MFA) and GSSAPI are accepted, so sshpass cannot work. The
# daemon authenticates via paramiko, auto-sends Duo Push, and holds one SSH
# session open indefinitely with auto-reconnect.
#
# Idempotent: if the port is already serving and a daemon PID is recorded,
# this script does nothing.
#
# Usage:
#   bash build/code/tunnel_up.sh                 # default port 49600
#   WRDS_LOCAL_PORT=51234 bash build/code/tunnel_up.sh
#   WRDS_PYBIN=/path/to/python bash build/code/tunnel_up.sh
#
# The interpreter is auto-detected: the venv wrds-mcp is installed into, then
# $VIRTUAL_ENV, ~/.wrds-mcp-env, a repo .venv, then python3 on PATH. The first
# one that can import paramiko wins. Set WRDS_PYBIN to override.
#
# The first time you run this you'll get a Duo Push -- approve on your phone.
# After that the tunnel survives until you run tunnel_down.sh or reboot.
#
# Logs:    ~/.wrds-tunnel/daemon.log
# PID:     ~/.wrds-tunnel/daemon.pid
set -euo pipefail

PORT="${WRDS_LOCAL_PORT:-49600}"
HERE="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="${WRDS_TUNNEL_STATE_DIR:-$HOME/.wrds-tunnel}"
PID_FILE="$RUN_DIR/daemon.pid"
LOG_FILE="$RUN_DIR/daemon.log"

mkdir -p "$RUN_DIR"

# ---------------------------------------------------------------------------
# Interpreter resolution.
#
# tunnel_daemon.py imports paramiko. The daemon is launched detached with its
# output redirected to the log, so an interpreter without paramiko used to die
# as a bare ModuleNotFoundError buried in daemon.log while this script reported
# only "daemon exited" -- 45 seconds later. Resolve and verify the interpreter
# up front instead, and say exactly how to fix it.
#
# Override with WRDS_PYBIN=/path/to/python; it is still verified.
# ---------------------------------------------------------------------------
has_paramiko() { [[ -x "$1" ]] && "$1" -c 'import paramiko' >/dev/null 2>&1; }

resolve_pybin() {
  if [[ -n "${WRDS_PYBIN:-}" ]]; then
    if has_paramiko "$WRDS_PYBIN"; then printf '%s' "$WRDS_PYBIN"; return 0; fi
    echo "ERROR: WRDS_PYBIN=$WRDS_PYBIN cannot import paramiko." >&2
    echo "       Install it there:  $WRDS_PYBIN -m pip install paramiko" >&2
    return 1
  fi

  local c entry candidates=()
  # Prefer the venv wrds-mcp itself was installed into, inferred from its
  # console script -- that env is guaranteed to have the server's deps.
  entry="$(command -v wrds-mcp 2>/dev/null || true)"
  [[ -n "$entry" ]] && candidates+=("$(dirname "$entry")/python3")
  [[ -n "${VIRTUAL_ENV:-}" ]] && candidates+=("$VIRTUAL_ENV/bin/python3")
  candidates+=(
    "$HOME/.wrds-mcp-env/bin/python3"
    "$HERE/../.venv/bin/python3"
    "$HERE/../../.venv/bin/python3"
    "$(command -v python3 2>/dev/null || true)"
    "$(command -v python  2>/dev/null || true)"
  )

  for c in "${candidates[@]}"; do
    [[ -n "$c" ]] || continue
    if has_paramiko "$c"; then printf '%s' "$c"; return 0; fi
  done

  {
    echo "ERROR: no Python interpreter with paramiko was found."
    echo
    echo "       tunnel_daemon.py needs paramiko: the WRDS bastion disables password"
    echo "       auth and accepts only Duo keyboard-interactive, which sshpass cannot do."
    echo
    echo "       Fix with either:"
    echo "         python3 -m pip install paramiko"
    echo "         WRDS_PYBIN=/path/to/python bash $0"
    echo
    echo "       Tried:"
    for c in "${candidates[@]}"; do [[ -n "$c" ]] && echo "         $c"; done
  } >&2
  return 1
}

PYBIN="$(resolve_pybin)" || exit 3

if [[ -z "${WRDS_USERNAME:-}" || -z "${WRDS_PASSWORD:-}" ]]; then
  echo "ERROR: WRDS_USERNAME and WRDS_PASSWORD must be exported." >&2
  exit 2
fi

# Already up?
if nc -z -w 2 127.0.0.1 "$PORT" 2>/dev/null; then
  if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "tunnel already up on 127.0.0.1:$PORT (pid $(cat "$PID_FILE"))"
    exit 0
  fi
  echo "WARNING: 127.0.0.1:$PORT is in use but no daemon PID recorded." >&2
  echo "         Run tunnel_down.sh or pick another port via WRDS_LOCAL_PORT." >&2
  exit 1
fi

# Stale PID?
if [[ -f "$PID_FILE" ]] && ! kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  rm -f "$PID_FILE"
fi

echo "starting tunnel daemon (paramiko) on port $PORT"
echo "  python: $PYBIN"
echo "  log: $LOG_FILE"
echo "  approve Duo Push on your phone within ~30s"

WRDS_LOCAL_PORT="$PORT" \
  nohup "$PYBIN" "$HERE/tunnel_daemon.py" \
  >>"$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

# Wait up to 45s for the forward to come up (Duo approval window).
for _ in $(seq 1 45); do
  if nc -z -w 2 127.0.0.1 "$PORT" 2>/dev/null; then
    echo "tunnel up on 127.0.0.1:$PORT (pid $(cat "$PID_FILE"))"
    exit 0
  fi
  if ! kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "ERROR: daemon exited. Tail of log:" >&2
    tail -20 "$LOG_FILE" >&2 || true
    rm -f "$PID_FILE"
    exit 1
  fi
  sleep 1
done

echo "ERROR: tunnel did not come up within 45s. Tail of log:" >&2
tail -30 "$LOG_FILE" >&2 || true
exit 1
