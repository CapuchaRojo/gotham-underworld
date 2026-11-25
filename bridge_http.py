"""Loopback-only C1 JSON API. No assets, filesystem routes or React integration."""
import argparse
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import secrets
import socket
import threading
import time
from urllib.parse import urlsplit

from bridge_checkpoint import BridgeError, VERSION, decode_json
from engine_bridge import Bridge

MAX_REQUEST_BYTES = 16384
REJECTION_DRAIN_SECONDS = 0.2


class BridgeServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, bridge, port=0, *, handler_class=None):
        if type(port) is not int or not 0 <= port <= 65535:
            raise ValueError('Invalid loopback port')
        self.bridge = bridge
        self.capability = secrets.token_urlsafe(32)
        self._slots = threading.BoundedSemaphore(8)
        super().__init__(('127.0.0.1', port), Handler if handler_class is None else handler_class)
        self.authority = f'127.0.0.1:{self.server_port}'
        self.origin = 'http://' + self.authority

    def process_request(self, request, address):
        if not self._slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, address)
        except BaseException:
            self._slots.release()
            raise

    def process_request_thread(self, request, address):
        try:
            super().process_request_thread(request, address)
        finally:
            self._slots.release()


class Handler(BaseHTTPRequestHandler):
    server_version = 'GoonBridge/1'

    def __getattr__(self, name):
        # The stdlib otherwise sends HTML 501 before our authorization path.
        # Parsing failures still use the stdlib parser's separate error path.
        if name.startswith('do_'):
            return self._dispatch
        raise AttributeError(name)

    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, *args):
        pass  # Never log capabilities, URLs or request bodies.

    def _send(self, status, data):
        body = json.dumps(data, allow_nan=False).encode('utf-8')
        try:
            self._write_response(status, body)
        except (ConnectionError, TimeoutError):
            self.close_connection = True  # A lost connection cannot undo a receipt.

    def _write_response(self, status, body):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'none'; frame-ancestors 'none'")
        self.send_header('Connection', 'close')
        if status == 405:
            self.send_header('Allow', 'GET, POST')
        self.end_headers()
        self.close_connection = True
        if self.command != 'HEAD':
            self.wfile.write(body)

    def _discard_body(self):
        # Send the rejection before waiting for untrusted input. A write-side FIN
        # lets the client read it while we discard delayed/buffered bytes. Never
        # trust a rejected Content-Length or wait for a peer to finish its body.
        try:
            self.wfile.flush()
            self.connection.shutdown(socket.SHUT_WR)
            deadline = time.monotonic() + REJECTION_DRAIN_SECONDS
            remaining = MAX_REQUEST_BYTES
            while remaining:
                timeout = deadline - time.monotonic()
                if timeout <= 0:
                    break
                self.connection.settimeout(timeout)
                chunk = self.rfile.read1(min(remaining, 4096))
                if not chunk:
                    break
                remaining -= len(chunk)
        except OSError:
            pass  # Socket teardown only: disconnects/timeouts cannot undo state.

    def _authorize(self):
        for name in ('Host', 'Origin', 'Authorization', 'Content-Length', 'Content-Type', 'Sec-Fetch-Site'):
            if len(self.headers.get_all(name, [])) > 1:
                raise BridgeError('INVALID_HEADERS', 'Duplicate request headers.')
        if self.headers.get('Host') != self.server.authority:
            raise BridgeError('UNSAFE_HOST', 'Unexpected loopback Host.', 403)
        authorization = self.headers.get('Authorization', '')
        if not hmac.compare_digest(authorization.encode('utf-8'), ('Bearer ' + self.server.capability).encode('ascii')):
            raise BridgeError('UNAUTHORIZED', 'Session capability required.', 401)
        origin = self.headers.get('Origin')
        if (origin is not None and origin != self.server.origin) or (self.command == 'POST' and origin is None):
            raise BridgeError('UNSAFE_ORIGIN', 'Same-origin browser request required.', 403)
        if self.headers.get('Sec-Fetch-Site') not in (None, 'same-origin', 'none'):
            raise BridgeError('UNSAFE_ORIGIN', 'Cross-site requests are not supported.', 403)
        if self.headers.get('Transfer-Encoding') is not None:
            raise BridgeError('INVALID_HEADERS', 'Transfer encodings are not supported.')

    def _body(self, limit=MAX_REQUEST_BYTES):
        length = self.headers.get('Content-Length', '')
        if not length.isascii() or not length.isdecimal() or len(length) > 8:
            raise BridgeError('INVALID_LENGTH', 'A bounded Content-Length is required.')
        length = int(length)
        if length > limit:
            raise BridgeError('REQUEST_TOO_LARGE', f'Request exceeds {limit} bytes.', 413)
        if self.headers.get('Content-Type', '').lower() != 'application/json':
            raise BridgeError('INVALID_CONTENT_TYPE', 'Expected application/json.', 415)
        try:
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise ValueError('short body')
            return decode_json(raw.decode('utf-8'))
        except (UnicodeError, ValueError, TimeoutError) as exc:
            raise BridgeError('MALFORMED_JSON', 'Expected a complete UTF-8 JSON body.') from exc

    def _dispatch(self):
        try:
            self._authorize()
            if self.command not in ('GET', 'POST'):
                raise BridgeError('METHOD_NOT_ALLOWED', 'Only GET and POST are supported.', 405)
            url = urlsplit(self.path)
            if url.scheme or url.netloc or url.query or url.fragment:
                raise BridgeError('INVALID_PATH', 'Only exact API paths are supported.', 404)
            path = url.path
            if self.command == 'GET':
                if self.headers.get('Content-Length') not in (None, '0'):
                    raise BridgeError('INVALID_LENGTH', 'GET bodies are not supported.')
                if path == '/api/v1/state':
                    result = self.server.bridge.state()
                elif path == '/api/v1/housing' or path.startswith('/api/v1/housing/operations/'):
                    if self.requestline.split()[1] != path:
                        raise BridgeError('INVALID_PATH', 'Only exact API paths are supported.', 404)
                    if path == '/api/v1/housing':
                        result = self.server.bridge.housing()
                    else:
                        request_id = path.removeprefix('/api/v1/housing/operations/')
                        if not request_id or '/' in request_id:
                            raise BridgeError('NOT_FOUND', 'Unknown API path.', 404)
                        result = self.server.bridge.housing_operation(request_id)
                elif path.startswith('/api/v1/operations/'):
                    result = self.server.bridge.operation(path[len('/api/v1/operations/'):])
                else:
                    raise BridgeError('NOT_FOUND', 'Unknown API path.', 404)
            elif self.command == 'POST':
                if path not in ('/api/v1/commands', '/api/v1/travel-quotes'):
                    raise BridgeError('NOT_FOUND', 'Unknown API path.', 404)
                body = self._body()
                if path == '/api/v1/commands':
                    result = self.server.bridge.execute(body)
                else:
                    if type(body) is not dict or set(body) != {'protocol_version', 'destination', 'mode'}:
                        raise BridgeError('INVALID_REQUEST', 'Quote requires protocol_version, destination and mode.')
                    if type(body['protocol_version']) is not int or body['protocol_version'] != VERSION:
                        raise BridgeError('PROTOCOL_MISMATCH', 'Supported protocol version: 1.', 409)
                    result = self.server.bridge.route(body['destination'], body['mode'])
            self._send(200, result)
        except BridgeError as exc:
            self._send(exc.status, dict(protocol_version=VERSION, error=dict(code=exc.code, message=str(exc))))
            self._discard_body()
        except ConnectionError:
            pass  # The committed receipt, not this connection, owns recovery.
        except Exception:
            self._send(500, dict(protocol_version=VERSION,
                                 error=dict(code='INTERNAL_ERROR', message='Local request failed.')))

    do_GET = _dispatch
    do_POST = _dispatch
    do_OPTIONS = _dispatch
    do_PUT = _dispatch
    do_DELETE = _dispatch
    do_PATCH = _dispatch
    do_HEAD = _dispatch


def main():
    parser = argparse.ArgumentParser(description='Offline C1 engine bridge; no frontend is served.')
    parser.add_argument('--checkpoint', required=True)
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--new', action='store_true')
    source.add_argument('--import-save')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--export-save', help='Exclusive legacy export, then exit without starting HTTP')
    parser.add_argument('--port', type=int, default=0)
    args = parser.parse_args()
    try:
        bridge = (Bridge.create(args.checkpoint, args.seed) if args.new else
                  Bridge.import_legacy(args.import_save, args.checkpoint) if args.import_save else
                  Bridge.open(args.checkpoint))
        with bridge:
            if args.export_save:
                bridge.export_legacy(args.export_save)
                print('Exported a new engine-compatible JSON save.')
                return
            with BridgeServer(bridge, args.port) as server:
                print('Local API:', server.origin, flush=True)
                print('Session capability (private):', server.capability, flush=True)
                try:
                    server.serve_forever()
                except KeyboardInterrupt:
                    pass
    except (BridgeError, OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
