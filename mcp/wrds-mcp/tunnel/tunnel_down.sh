#!/usr/bin/env bash
# tunnel_down.sh -- stop the paramiko tunnel daemon.
set -euo pipefail
RUN_DIR="${WRDS_TUNNEL_STATE_DIR:-$HOME/.wrds-tunnel}"
PID_FILE="$RUN_DIR/daemon.pid"
PORT="${WRDS_LOCAL_PORT:-49600}"

stopped=0

if [[ -f "$PID_FILE" ]]; then
  pid="$(cat "$PID_FILE")"
  if kill -0 "$pid" 2>/dev/null; then
    echo "stopping tunnel daemon pid $pid"
    kill "$pid" 2>/dev/null || true
    for _ in $(seq 1 10); do
      kill -0 "$pid" 2>/dev/null || { stopped=1; break; }
      sleep 1
    done
    if [[ $stopped -eq 0 ]]; then
      echo "  daemon did not exit on SIGTERM; sending SIGKILL"
      kill -9 "$pid" 2>/dev/null || true
    fi
  else
    echo "stale PID file (pid $pid not running)"
  fi
  rm -f "$PID_FILE"
fi

# Belt-and-suspenders: any leftover python tunnel_daemon.py processes for this port?
leftover="$(pgrep -f "tunnel_daemon\.py" 2>/dev/null || true)"
if [[ -n "$leftover" ]]; then
  echo "killing leftover tunnel_daemon.py pids: $leftover"
  kill $leftover 2>/dev/null || true
fi

if nc -z -w 2 127.0.0.1 "$PORT" 2>/dev/null; then
  echo "WARNING: 127.0.0.1:$PORT still has a listener after kill." >&2
  exit 1
fi
echo "tunnel down (port $PORT closed)"
