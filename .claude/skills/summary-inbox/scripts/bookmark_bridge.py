#!/usr/bin/env python3
"""
Summary Inbox Bookmark Bridge

Native Messaging Host for Chrome Extension communication.
Spawns a Unix socket server so CLI tools can send commands through
to the Chrome extension's chrome.bookmarks API.

Two modes:
  1) Native Messaging Host (default) — Chrome spawns this, reads/writes stdin/stdout
  2) CLI mode: python bookmark_bridge.py <command> [args...]
"""
import json
import struct
import sys
import os
import threading
import socket
import time
import uuid
from pathlib import Path

SOCKET_PATH = '/tmp/chrome-summary-inbox.sock'
BUFFER_SIZE = 65536

# --- Native Messaging Protocol ---

def read_native_message():
    """Read a JSON message from Chrome via stdin (length-prefixed)."""
    raw = sys.stdin.buffer.read(4)
    if not raw or len(raw) < 4:
        return None
    length = struct.unpack('I', raw)[0]
    if length == 0:
        return None
    payload = sys.stdin.buffer.read(length)
    return json.loads(payload)


def write_native_message(data):
    """Write a JSON message to Chrome via stdout (length-prefixed)."""
    payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('I', len(payload)))
    sys.stdout.buffer.write(payload)
    sys.stdout.buffer.flush()


# --- Unix Socket Server (for CLI communication) ---

class BridgeServer:
    def __init__(self):
        self.pending = {}
        self.lock = threading.Lock()
        self.ready = threading.Event()

    def handle_cli(self, conn):
        """Handle a single CLI connection."""
        try:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                return
            request = json.loads(data.decode('utf-8'))
            req_id = request.get('id', str(uuid.uuid4()))
            request['id'] = req_id

            result_event = threading.Event()
            result_container = [None]

            with self.lock:
                self.pending[req_id] = (result_event, result_container)

            # Forward to extension via native messaging
            write_native_message(request)

            # Wait for response (with timeout)
            if result_event.wait(timeout=30):
                response = json.dumps(result_container[0], ensure_ascii=False)
                conn.sendall(response.encode('utf-8'))
            else:
                conn.sendall(json.dumps({'status': 'error', 'error': 'timeout'}).encode('utf-8'))
                with self.lock:
                    self.pending.pop(req_id, None)
        except Exception as e:
            try:
                conn.sendall(json.dumps({'status': 'error', 'error': str(e)}).encode('utf-8'))
            except Exception:
                pass
        finally:
            conn.close()

    def deliver_response(self, response):
        """Deliver a response from the extension to the waiting CLI."""
        response_to = response.get('responseTo')
        if not response_to:
            return
        with self.lock:
            entry = self.pending.pop(response_to, None)
        if entry:
            event, container = entry
            container[0] = response
            event.set()


def run_socket_server(server):
    """Run the Unix socket server in a daemon thread."""
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(SOCKET_PATH)
    sock.listen(5)
    os.chmod(SOCKET_PATH, 0o600)
    server.ready.set()

    while True:
        try:
            conn, _ = sock.accept()
            t = threading.Thread(target=server.handle_cli, args=(conn,), daemon=True)
            t.start()
        except Exception:
            time.sleep(0.1)


# --- CLI Mode ---

def run_cli():
    """CLI mode: connect to running daemon, send command, get response."""
    if not os.path.exists(SOCKET_PATH):
        print("Error: Bridge daemon is not running.", file=sys.stderr)
        print("Make sure Chrome is running with the Summary Inbox Bridge extension loaded.", file=sys.stderr)
        sys.exit(1)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(10)
    try:
        sock.connect(SOCKET_PATH)
    except ConnectionRefusedError:
        print("Error: Bridge daemon unreachable. Try restarting Chrome.", file=sys.stderr)
        sys.exit(1)

    # Parse command
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    # Support: bookmark_bridge.py moveBookmark --url https://... [--target Archives]
    # Or direct JSON command via --json '{"cmd": ...}'

    if not args:
        print("Usage: bookmark_bridge.py <command> [args...]", file=sys.stderr)
        print("       bookmark_bridge.py --json '{\"cmd\": \"...\"}'", file=sys.stderr)
        sys.exit(1)

    if args[0] == '--json':
        request = json.loads(args[1])
    elif args[0] == 'moveBookmark':
        url = None
        target = 'Archives'
        for i, a in enumerate(args[1:], 1):
            if a == '--url' and i + 1 < len(args):
                url = args[i + 1]
            if a == '--target' and i + 1 < len(args):
                target = args[i + 1]
        if not url:
            print("Error: --url is required for moveBookmark", file=sys.stderr)
            sys.exit(1)
        request = {'cmd': 'moveBookmark', 'url': url, 'targetFolder': target}
    elif args[0] == 'listFolder':
        folder = args[1] if len(args) > 1 else 'Inbox'
        request = {'cmd': 'listFolder', 'name': folder}
    elif args[0] == 'findFolder':
        name = args[1] if len(args) > 1 else 'Archives'
        request = {'cmd': 'findFolder', 'name': name}
    elif args[0] == 'createFolder':
        name = args[1] if len(args) > 1 else 'Archives'
        parent_id = args[2] if len(args) > 2 else '2'
        request = {'cmd': 'createFolder', 'name': name, 'parentId': parent_id}
    else:
        print(f"Unknown command: {args[0]}", file=sys.stderr)
        sys.exit(1)

    request['id'] = str(uuid.uuid4())
    payload = json.dumps(request, ensure_ascii=False).encode('utf-8')
    sock.sendall(payload)

    # Read response (the daemon sends length-prefixed data via Unix socket)
    response = b''
    while True:
        try:
            chunk = sock.recv(65536)
            if not chunk:
                break
            response += chunk
            # Try to parse — if complete JSON, we're done
            try:
                json.loads(response)
                break
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
        except socket.timeout:
            break

    sock.close()
    result = json.loads(response) if response else {'status': 'error', 'error': 'no response'}
    print(json.dumps(result, ensure_ascii=False, indent=2))


# --- Main ---

def main():
    # If invoked with CLI args, run as CLI client
    if len(sys.argv) > 1 and sys.argv[1] not in ('--daemon',):
        run_cli()
        return

    # Native Messaging Host mode — spawned by Chrome
    server = BridgeServer()

    # Start socket server in background
    t = threading.Thread(target=run_socket_server, args=(server,), daemon=True)
    t.start()

    # Wait for socket to be ready
    server.ready.wait(timeout=5)

    # Tell extension we're ready
    write_native_message({'event': 'ready'})

    # Main loop: read messages from extension
    try:
        while True:
            msg = read_native_message()
            if msg is None:
                break
            server.deliver_response(msg)
    except (EOFError, BrokenPipeError, KeyboardInterrupt):
        pass
    finally:
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)


if __name__ == '__main__':
    main()
