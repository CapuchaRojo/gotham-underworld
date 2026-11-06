"""Opt-in offline browser host; existing checkpoints only, no React integration."""
import argparse
from contextlib import closing
import json
import os
from pathlib import Path
import secrets
import socket
import stat
import tempfile
import threading
from urllib.parse import urlsplit
import webbrowser

from bridge_assets import CONTENT_POLICY, ENGINE_RELEASE, HOST_VERSION, load_bundle
from bridge_bootstrap import BOOTSTRAP_BYTES, Bootstrap
from bridge_checkpoint import BridgeError, CareerLock, VERSION, decode_json, storage_paths
from bridge_http import BridgeServer, Handler
from engine_bridge import Bridge

MAX_URL = 2048


class BrowserHandler(Handler):
    def _context(self):
        # Public assets are not permission to access the engine. Keep the API's
        # original authorization path below entirely intact.
        for name in ('Host', 'Origin', 'Authorization', 'Content-Length', 'Content-Type', 'Sec-Fetch-Site'):
            if len(self.headers.get_all(name, [])) > 1:
                raise BridgeError('INVALID_HEADERS', 'Duplicate request headers.')
        if self.headers.get('Host') != self.server.authority:
            raise BridgeError('UNSAFE_HOST', 'Unexpected loopback Host.', 403)
        origin = self.headers.get('Origin')
        if (origin is not None and origin != self.server.origin) or (self.command == 'POST' and origin is None):
            raise BridgeError('UNSAFE_ORIGIN', 'Same-origin browser request required.', 403)
        if self.headers.get('Sec-Fetch-Site') not in (None, 'same-origin', 'none'):
            raise BridgeError('UNSAFE_ORIGIN', 'Cross-site requests are not supported.', 403)
        if self.headers.get('Transfer-Encoding') is not None:
            raise BridgeError('INVALID_HEADERS', 'Transfer encodings are not supported.')

    def _asset(self, asset):
        self.send_response(200)
        for key, value in {'Content-Type': asset.mime, 'Content-Length': str(len(asset.body)),
                           'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff',
                           'Content-Security-Policy': CONTENT_POLICY, 'Referrer-Policy': 'no-referrer',
                           'Cross-Origin-Resource-Policy': 'same-origin',
                           'Cross-Origin-Opener-Policy': 'same-origin', 'Connection': 'close'}.items():
            self.send_header(key, value)
        self.end_headers()
        self.close_connection = True
        self.wfile.write(asset.body)

    def _dispatch(self):
        # Engine routes retain the original parser/authentication/receipt path.
        if self.path.startswith('/api/') and len(self.path) <= MAX_URL:
            return super()._dispatch()
        try:
            self._context()
            url = urlsplit(self.path)
            if (len(self.path) > MAX_URL or url.scheme or url.netloc or url.query or url.fragment or
                    '%' in self.path or '\\' in self.path or any(ord(c) < 32 for c in self.path)):
                raise BridgeError('INVALID_PATH', 'Only exact host paths are supported.', 404)
            if self.command not in ('GET', 'POST'):
                # Even unsupported host requests require the existing capability.
                self._authorize()
                raise BridgeError('METHOD_NOT_ALLOWED', 'Only GET and POST are supported.', 405)
            if self.command == 'GET' and self.headers.get('Content-Length') not in (None, '0'):
                raise BridgeError('INVALID_LENGTH', 'GET bodies are not supported.')
            if url.path == '/host/v1/bootstrap':
                if self.command != 'POST':
                    raise BridgeError('METHOD_NOT_ALLOWED', 'Bootstrap requires POST.', 405)
                request = self._body(BOOTSTRAP_BYTES)
                if (type(request) is not dict or set(request) != {'host_protocol_version', 'bundle_id', 'code'} or
                        type(request['host_protocol_version']) is not int or request['host_protocol_version'] != HOST_VERSION or
                        request['bundle_id'] != self.server.bundle.bundle_id):
                    raise BridgeError('HOST_INCOMPATIBLE', 'Browser bundle or host protocol is incompatible.', 409)
                capability = self.server.bootstrap.redeem(request['code'])
                self._send(200, dict(self.server.session(), capability=capability))
            elif url.path == '/host/v1/session':
                self._authorize()
                if self.command != 'GET':
                    raise BridgeError('METHOD_NOT_ALLOWED', 'Session inspection requires GET.', 405)
                self._send(200, self.server.session())
            elif url.path in self.server.bundle.assets:
                if self.command != 'GET':
                    raise BridgeError('METHOD_NOT_ALLOWED', 'Assets require GET.', 405)
                self._asset(self.server.bundle.assets[url.path])
            else:
                raise BridgeError('NOT_FOUND', 'Unknown host path.', 404)
        except BridgeError as exc:
            self._send(exc.status, dict(host_protocol_version=HOST_VERSION,
                                       error=dict(code=exc.code, message=str(exc))))
            self._discard_body()
        except (ConnectionError, TimeoutError):
            pass  # Socket loss cannot execute or undo a gameplay command.
        except Exception:
            self._send(500, dict(host_protocol_version=HOST_VERSION,
                                 error=dict(code='INTERNAL_ERROR', message='Local host request failed.')))

    do_GET = _dispatch
    do_POST = _dispatch
    do_OPTIONS = _dispatch
    do_PUT = _dispatch
    do_DELETE = _dispatch
    do_PATCH = _dispatch
    do_HEAD = _dispatch


class BrowserServer(BridgeServer):
    def __init__(self, bridge, bundle, port=0):
        self.bundle = bundle
        self.instance_id = secrets.token_hex(16)
        super().__init__(bridge, port, handler_class=BrowserHandler)
        self.bootstrap = Bootstrap(self.capability)

    def server_bind(self):
        if os.name == 'nt':
            # SO_REUSEADDR on Windows can admit another listener on our port.
            self.allow_reuse_address = False
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()

    def session(self):
        return dict(host_protocol_version=HOST_VERSION, bridge_protocol_version=VERSION,
                    bundle_id=self.bundle.bundle_id, manifest_sha256=self.bundle.manifest_sha256,
                    engine_release=ENGINE_RELEASE, instance_id=self.instance_id,
                    mode='local_engine', session_lifetime='process')


def _config_port(path):
    if path.is_symlink() or (path.exists() and getattr(path.lstat(), 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
        raise ValueError('Invalid host configuration')
    if not path.exists():
        return 0
    if path.stat().st_size > 1024:
        raise ValueError('Invalid host configuration')
    config = decode_json(path.read_text(encoding='utf-8'))
    if (type(config) is not dict or set(config) != {'host_config_version', 'port'} or
            type(config['host_config_version']) is not int or config['host_config_version'] != 1 or
            type(config['port']) is not int or not 1 <= config['port'] <= 65535):
        raise ValueError('Invalid host configuration')
    return config['port']


def _publish_config(path, port):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.' + path.name, suffix='.tmp',
                                         mode='wb', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(json.dumps(dict(host_config_version=1, port=port)).encode('utf-8'))
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)  # Exclusive: never replace a competing config.
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class BrowserHost:
    def __init__(self, server, bridge):
        self.server, self.bridge = server, bridge
        self._thread = None
        self._closed = False

    @classmethod
    def open(cls, checkpoint, config_path, bundle):
        """Reserve the stored port before opening a career; never create/import one."""
        checkpoint, config = Path(checkpoint).resolve(), Path(config_path).absolute()
        if storage_paths(checkpoint) & storage_paths(config):
            raise BridgeError('INVALID_PATH', 'Host configuration must be separate from career storage.')
        config.parent.mkdir(parents=True, exist_ok=True)
        server = bridge = None
        try:
            with closing(CareerLock(config)):
                port = _config_port(config)
                server = BrowserServer(None, bundle, port)
                if not port:
                    _publish_config(config, server.server_port)
                bridge = Bridge.open(checkpoint)
                server.bridge = bridge
            return cls(server, bridge)
        except BaseException:
            if server is not None:
                server.bootstrap.close()
                server.server_close()
            if bridge is not None:
                bridge.close()
            raise

    def start(self):
        if self._closed or self._thread is not None:
            raise ValueError('Host is closed or already started')
        thread = threading.Thread(target=lambda: self.server.serve_forever(poll_interval=0.05), daemon=True)
        thread.start()
        self._thread = thread

    def close(self):
        if self._closed:
            return
        self._closed = True
        self.server.bootstrap.close()
        self.server.capability = secrets.token_urlsafe(32)
        if self._thread is not None:
            self.server.shutdown()
            self._thread.join()
        self.server.server_close()
        self.bridge.close()  # Waits for any already-authorized atomic mutation.

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def main():
    parser = argparse.ArgumentParser(description='Verified local browser host; existing careers only.')
    parser.add_argument('--checkpoint', required=True)
    parser.add_argument('--bundle-id', required=True)
    parser.add_argument('--manifest-sha256', required=True, help='Trusted release pin, not an automatically accepted manifest hash')
    default = Path(os.environ.get('LOCALAPPDATA', Path.home() / '.local' / 'share')) / 'GothamTheGoon' / 'browser-host.json'
    parser.add_argument('--host-config', type=Path, default=default)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    try:
        bundle = load_bundle(Path(__file__).absolute().parent, args.bundle_id, args.manifest_sha256)
        with BrowserHost.open(args.checkpoint, args.host_config, bundle) as host:
            host.start()
            print('Local application:', host.server.origin, flush=True)
            print('One-time authorization code (120 seconds):', host.server.bootstrap.issue(), flush=True)
            if not args.no_browser:
                webbrowser.open(host.server.origin + '/', new=2)
            try:
                while True:
                    value = input('Enter for a new authorization code; quit to stop: ')
                    if value.strip().lower() == 'quit':
                        break
                    print('One-time authorization code (120 seconds):', host.server.bootstrap.issue(), flush=True)
            except (EOFError, KeyboardInterrupt):
                pass
    except (BridgeError, OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
