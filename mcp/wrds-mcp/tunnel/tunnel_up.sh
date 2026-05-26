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
PYBIN="${WRDS_PYBIN:-python3}"

mkdir -p "$RUN_DIR"

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
