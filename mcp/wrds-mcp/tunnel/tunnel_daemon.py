#!/usr/bin/env python3
"""tunnel_daemon.py -- persistent paramiko-based SSH tunnel to WRDS Postgres.

Holds ONE long-lived keyboard-interactive SSH session to wrds-cloud.wharton.upenn.edu
and forwards 127.0.0.1:$WRDS_LOCAL_PORT -> wrds-pgdata.wharton.upenn.edu:9737.
Approve Duo Push once at startup; the tunnel then survives indefinitely (with
auto-reconnect on drop).

Why this instead of autossh+sshpass:
  WRDS-cloud bastion has password-auth disabled. Only `keyboard-interactive`
  (which is how Duo MFA is delivered) and GSSAPI are accepted, so sshpass
  cannot authenticate. paramiko handles keyboard-interactive natively.

Usage:
  # Foreground (interactive — approve Duo on phone, watch logs)
  python build/code/tunnel_daemon.py

  # Background, via the wrapper:
  bash build/code/tunnel_up.sh

Environment:
  WRDS_USERNAME           (required)  WRDS login (your WRDS username, e.g. jsmith_univ)
  WRDS_PASSWORD           (required)  WRDS password — fed to keyboard-interactive
  WRDS_LOCAL_PORT         (default 49600)  local listen port
  WRDS_DUO_RESPONSE       (default 'push')  what to send to Duo prompt: 'push',
                                            'phone', or a numeric passcode
  WRDS_MAX_RECONNECTS     (default 20)  hard cap on reconnect attempts before
                                        the daemon exits — prevents 3am Duo
                                        Push storms if WRDS auth keeps failing
"""
from __future__ import annotations
import os
import sys
import time
import socket
import signal
import logging
import threading
from typing import Optional

import paramiko

WRDS_SSH_HOST = "wrds-cloud.wharton.upenn.edu"
WRDS_PG_HOST = "wrds-pgdata.wharton.upenn.edu"
WRDS_PG_PORT = 9737

# Keywords that mark a prompt as the Duo / second-factor step. Wharton has
# rotated through several wordings; cover all of them. The fallback for an
# unrecognized prompt is empty string (NEVER the password — paramiko logs all
# keyboard-interactive responses, and a misrouted password gets flagged by
# Duo as a failed MFA and rate-limits the account).
DUO_KEYWORDS = (
    "duo", "passcode", "option", "choose", "choice",
    "two-factor", "authenticate", "verify", "second",
)

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger("tunnel_daemon")


class WRDSTunnel:
    def __init__(self, username: str, password: str, local_port: int, duo_response: str):
        self.username = username
        self.password = password
        self.local_port = local_port
        self.duo_response = duo_response
        self.transport: Optional[paramiko.Transport] = None
        self.server_socket: Optional[socket.socket] = None
        self.running = False

    def _ki_handler(self, title, instructions, prompt_list):
        out = []
        for prompt_text, _echo in prompt_list:
            p = prompt_text.lower().strip()
            if "password" in p:
                out.append(self.password)
            elif any(k in p for k in DUO_KEYWORDS):
                log.info("Duo prompt detected (%r) — sending '%s'. Approve on your phone.",
                         prompt_text.strip(), self.duo_response)
                out.append(self.duo_response)
            else:
                # Unknown prompt: send empty rather than leaking the password
                # into Duo logs / unrecognized auth steps.
                log.warning("unknown auth prompt %r — sending empty response", prompt_text.strip())
                out.append("")
        return out

    def authenticate(self):
        log.info("opening SSH connection to %s", WRDS_SSH_HOST)
        self.transport = paramiko.Transport((WRDS_SSH_HOST, 22))
        self.transport.set_keepalive(30)
        self.transport.connect()
        self.transport.auth_interactive(self.username, self._ki_handler)
        if not self.transport.is_authenticated():
            raise ConnectionError("WRDS SSH auth failed (Duo not approved or wrong password?)")
        log.info("SSH authenticated as %s", self.username)

    def bind_local(self):
        if self.server_socket is not None:
            return
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", self.local_port))
        except OSError as e:
            log.error("could not bind 127.0.0.1:%d — is the daemon already running? (%s)",
                      self.local_port, e)
            s.close()
            sys.exit(3)
        s.listen(16)
        s.settimeout(1.0)
        self.server_socket = s
        log.info("listening on 127.0.0.1:%d -> %s:%d", self.local_port, WRDS_PG_HOST, WRDS_PG_PORT)

    @staticmethod
    def _pump(src, dst):
        """One-way forwarding from src to dst. On exit, force-shutdown the peer
        side so the matching reverse-pump's blocking recv wakes up promptly —
        otherwise paramiko Channel.recv() can hang past the SSH transport's EOF
        when the local TCP peer resets, leaking channels and threads."""
        try:
            while True:
                data = src.recv(8192)
                if not data:
                    break
                dst.sendall(data)
        except Exception:
            pass
        # Close write side of dst (works for both socket.socket and Channel —
        # both have shutdown(how)). This ensures the peer pump exits.
        try:
            dst.shutdown(socket.SHUT_WR)
        except Exception:
            pass
        try:
            src.close()
        except Exception:
            pass
        try:
            dst.close()
        except Exception:
            pass

    def accept_loop(self):
        """Run until the SSH transport dies. Returns to caller for reconnect."""
        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()
            except socket.timeout:
                if self.transport is None or not self.transport.is_active():
                    log.warning("transport dead; breaking accept loop to trigger reconnect")
                    return
                continue
            except OSError:
                return
            try:
                channel = self.transport.open_channel(
                    "direct-tcpip", (WRDS_PG_HOST, WRDS_PG_PORT), addr
                )
            except Exception as e:
                log.warning("could not open channel for %s: %s", addr, e)
                try:
                    client_sock.close()
                except Exception:
                    pass
                continue
            threading.Thread(target=self._pump, args=(client_sock, channel), daemon=True).start()
            threading.Thread(target=self._pump, args=(channel, client_sock), daemon=True).start()

    def shutdown(self):
        self.running = False
        if self.server_socket is not None:
            try:
                self.server_socket.close()
            except Exception:
                pass
            self.server_socket = None
        if self.transport is not None:
            try:
                self.transport.close()
            except Exception:
                pass
            self.transport = None


def main():
    username = os.environ.get("WRDS_USERNAME", "")
    password = os.environ.get("WRDS_PASSWORD", "")
    if not username or not password:
        log.error("WRDS_USERNAME and WRDS_PASSWORD must be set")
        sys.exit(2)

    local_port = int(os.environ.get("WRDS_LOCAL_PORT", "49600"))
    duo_response = os.environ.get("WRDS_DUO_RESPONSE", "push")
    max_reconnects = int(os.environ.get("WRDS_MAX_RECONNECTS", "20"))

    tunnel = WRDSTunnel(username, password, local_port, duo_response)

    def _shutdown(signum, _frame):
        log.info("signal %d received; shutting down", signum)
        tunnel.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    # Bind the listening socket BEFORE the auth loop. This way:
    #   (a) a port collision is reported on the first try, not after Duo;
    #   (b) on auth failures, clients hitting 49600 fail fast with a connection
    #       error rather than hanging waiting for the listener to appear.
    tunnel.bind_local()

    backoff = 5
    attempt = 0
    while True:
        attempt += 1
        if attempt > max_reconnects:
            log.error("reached WRDS_MAX_RECONNECTS=%d — giving up. Run tunnel_up.sh again.",
                      max_reconnects)
            tunnel.shutdown()
            sys.exit(4)
        try:
            tunnel.authenticate()
            tunnel.running = True
            backoff = 5  # reset on successful auth
            tunnel.accept_loop()
            log.warning("accept loop exited (transport dropped); will reconnect in %ds", backoff)
        except Exception as e:
            log.error("tunnel error on attempt %d/%d: %s", attempt, max_reconnects, e)
            log.warning("reconnecting in %ds (will trigger another Duo prompt)", backoff)
        # Tear down transport but keep listening socket bound across reconnects.
        if tunnel.transport is not None:
            try:
                tunnel.transport.close()
            except Exception:
                pass
            tunnel.transport = None
        time.sleep(backoff)
        backoff = min(backoff * 2, 60)


if __name__ == "__main__":
    main()
