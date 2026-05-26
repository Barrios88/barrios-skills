#!/usr/bin/env bash
# tunnel_status.sh -- report on the WRDS tunnel daemon.
set -euo pipefail
RUN_DIR="${WRDS_TUNNEL_STATE_DIR:-$HOME/.wrds-tunnel}"
PID_FILE="$RUN_DIR/daemon.pid"
LOG_FILE="$RUN_DIR/daemon.log"
PORT="${WRDS_LOCAL_PORT:-49600}"

echo "tunnel status (port $PORT):"

if [[ -f "$PID_FILE" ]]; then
  pid="$(cat "$PID_FILE")"
  if kill -0 "$pid" 2>/dev/null; then
    echo "  daemon: RUNNING (pid $pid)"
  else
    echo "  daemon: NOT RUNNING (stale PID file)"
  fi
else
  echo "  daemon: NO PID FILE"
fi

if nc -z -w 2 127.0.0.1 "$PORT" 2>/dev/null; then
  echo "  port:   OPEN"
else
  echo "  port:   CLOSED"
  if [[ -f "$LOG_FILE" ]]; then
    echo "  last 10 lines of $LOG_FILE:"
    tail -10 "$LOG_FILE" | sed 's/^/    /'
  fi
  exit 1
fi

PSQL=/opt/homebrew/opt/libpq/bin/psql
if [[ -x "$PSQL" ]]; then
  echo "  round-trip:"
  PGPASSWORD="${WRDS_PASSWORD}" "$PSQL" \
    "host=127.0.0.1 port=$PORT dbname=wrds user=${WRDS_USERNAME:?WRDS_USERNAME must be set} sslmode=require connect_timeout=10" \
    -t -c "select 'wrds ok' as status, current_user, current_database();" 2>&1 \
    | sed 's/^/    /'
fi
