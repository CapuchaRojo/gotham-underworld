"""Synthetic assets only. No assertion here establishes React/browser compatibility."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import hashlib
import http.client
import io
import json
import os
from pathlib import Path
import random
import socket
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import bridge_assets as assets
import game_service as engine
from bridge_bootstrap import Bootstrap, MAX_ATTEMPTS, CODE_SECONDS
from bridge_checkpoint import BridgeError, decode_json
from bridge_http import BridgeServer
from browser_host import BrowserHost, BrowserServer, main
from engine_bridge import Bridge


def fixture(app, bundle_id='host-test'):
    """This is a deliberately synthetic host fixture, not a compiled game UI."""
    root = app / 'ui_dist' / bundle_id
    public = root / 'public'
    (public / 'assets').mkdir(parents=True)
    files = {'index.html': b'<!doctype html><title>Synthetic host test</title><script src="/assets/test.js"></script>',
             'assets/test.js': b'/* Synthetic host fixture. No gameplay client. */',
             'assets/test.css': b'body { color: white; }'}
    rows = []
    for name, body in files.items():
        (public / name).write_bytes(body)
        mime = assets.HTML_MIME if name == 'index.html' else assets.MIME_TYPES[Path(name).suffix]
        rows.append(dict(path=name, size=len(body), sha256=hashlib.sha256(body).hexdigest(), mime=mime))
    manifest = dict(asset_manifest_version=1, host_protocol_version=1, bridge_protocol_version=1,
                    engine_release=assets.ENGINE_RELEASE, bundle_id=bundle_id, mode='local_engine', files=rows)
    return root, manifest


def pin(root, manifest):
    raw = json.dumps(manifest).encode()
    (root / 'manifest.json').write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


class AssetTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.app = Path(self.folder.name)
        self.root, self.manifest = fixture(self.app)
        self.pin = pin(self.root, self.manifest)

    def load(self, manifest=None):
        digest = self.pin if manifest is None else pin(self.root, manifest)
        return assets.load_bundle(self.app, 'host-test', digest)

    def load_index(self, body):
        (self.root / 'public/index.html').write_bytes(body)
        manifest = deepcopy(self.manifest)
        manifest['files'][0].update(size=len(body), sha256=hashlib.sha256(body).hexdigest())
        return self.load(manifest)

    def test_verified_bytes_are_immutable_and_detached_from_filesystem(self):
        bundle = self.load()
        self.assertEqual(set(bundle.assets), {'/', '/assets/test.js', '/assets/test.css'})
        body = bundle.assets['/assets/test.js'].body
        (self.root / 'public/assets/test.js').write_bytes(b'changed after verification')
        self.assertEqual(bundle.assets['/assets/test.js'].body, body)
        with self.assertRaises(TypeError):
            bundle.assets['/secret'] = bundle.assets['/']

    def test_pin_and_content_corruption_fail_closed(self):
        with self.assertRaises(BridgeError):
            assets.load_bundle(self.app, 'host-test', '0' * 64)
        (self.root / 'public/assets/test.js').write_bytes(b'bad')
        with self.assertRaises(BridgeError):
            self.load()

    def test_missing_manifest_asset_and_index_fail_closed(self):
        target = self.root / 'public/index.html'
        original = target.read_bytes()
        target.unlink()
        with self.assertRaises(BridgeError): self.load()
        target.write_bytes(original)
        manifest = deepcopy(self.manifest)
        manifest['files'] = manifest['files'][1:]
        with self.assertRaises(BridgeError): self.load(manifest)
        (self.root / 'manifest.json').unlink()
        with self.assertRaises(BridgeError): self.load()

    def test_protocol_mode_release_and_field_mismatches_are_rejected(self):
        for key, value in [('asset_manifest_version', True), ('host_protocol_version', 2),
                           ('bridge_protocol_version', 2), ('engine_release', 'wrong'),
                           ('bundle_id', 'different'), ('mode', 'synthetic'), ('extra', 'field')]:
            with self.subTest(key=key):
                changed = deepcopy(self.manifest)
                changed[key] = value
                with self.assertRaises(BridgeError): self.load(changed)

    def test_file_paths_mime_sizes_and_duplicate_rows_are_rejected(self):
        values = [('path', '../secret.js'), ('path', 'assets/../secret.js'), ('path', 'assets/test.js:secret'),
                  ('path', 'assets/test.py'), ('path', 'assets/test.js.map'), ('path', 'docs/private.js'),
                  ('path', 'assets/test.svg'), ('path', 'assets/%2e%2e.js'), ('mime', 'text/html'),
                  ('size', True), ('size', assets.MAX_FILE_BYTES + 1), ('sha256', 'bad')]
        for key, value in values:
            with self.subTest(key=key, value=value):
                changed = deepcopy(self.manifest)
                changed['files'][1][key] = value
                with self.assertRaises(BridgeError): self.load(changed)
        changed = deepcopy(self.manifest)
        changed['files'].append(changed['files'][0])
        with self.assertRaises(BridgeError): self.load(changed)

    def test_total_size_file_count_and_manifest_size_are_bounded(self):
        with patch('bridge_assets.MAX_BUNDLE_BYTES', 1), self.assertRaises(BridgeError): self.load()
        with patch('bridge_assets.MAX_FILES', 1), self.assertRaises(BridgeError): self.load()
        with patch('bridge_assets.MAX_MANIFEST_BYTES', 10), self.assertRaises(BridgeError): self.load()

    def test_unlisted_authoring_files_are_not_allowed_in_public_root(self):
        for name in ('game_service.py', 'save.json', 'notes.md', 'source.zip'):
            target = self.root / 'public' / name
            target.write_text('PRIVATE_SENTINEL')
            with self.subTest(name=name), self.assertRaises(BridgeError): self.load()
            target.unlink()

    def test_index_cannot_reference_missing_remote_source_or_inline_assets(self):
        for body in (b'<script src="/assets/missing.js"></script>',
                     b'<script src="/src/main.tsx"></script>',
                     b'<script src="https://example.com/script.js"></script>',
                     b'<script>console.log("inline")</script>', b'<div style="color:red">test</div>'):
            with self.subTest(body=body):
                with self.assertRaises(BridgeError): self.load_index(body)

    def test_index_rejects_duplicate_attributes_in_either_order(self):
        for body in (b'<script src="/assets/missing.js" src="/assets/test.js"></script>',
                     b'<script src="https://example.invalid/x.js" src="/assets/test.js"></script>',
                     b'<script src="/assets/test.js" src="/assets/missing.js"></script>',
                     b'<script src="/assets/test.js" src="https://example.invalid/x.js"></script>',
                     b'<script src="/assets/test.js" SRC="/assets/test.js"></script>',
                     b'<link href="/assets/missing.css" href="/assets/test.css">'):
            with self.subTest(body=body), self.assertRaises(BridgeError): self.load_index(body)

    def test_index_rejects_unsupported_resource_attributes(self):
        for body in (b'<img srcset="/assets/missing.png 1x">',
                     b'<img srcset="https://example.invalid/x.png 1x">',
                     b'<source srcset="/assets/missing.png 1x, https://example.invalid/x.png 2x">',
                     b'<link rel="preload" imagesrcset="https://example.invalid/x.png 1x">',
                     b'<video poster="/assets/missing.png"></video>',
                     b'<object data="https://example.invalid/x"></object>',
                     b'<body background="/assets/missing.png"></body>',
                     b'<html manifest="/assets/missing.appcache"></html>',
                     b'<a ping="https://example.invalid/x">link</a>',
                     b'<object codebase="https://example.invalid/"></object>',
                     b'<object archive="/assets/missing.jar"></object>',
                     b'<form action="https://example.invalid/"></form>',
                     b'<button formaction="https://example.invalid/">submit</button>'):
            with self.subTest(body=body), self.assertRaises(BridgeError): self.load_index(body)

    def test_index_preserves_approved_absolute_and_relative_references(self):
        for prefix in ('/', ''):
            body = (f'<script type="module" crossorigin src="{prefix}assets/test.js"></script>'
                    f'<link rel="stylesheet" href="{prefix}assets/test.css">'
                    '<div id="root" data-testid="host-fixture"></div>').encode()
            with self.subTest(prefix=prefix):
                bundle = self.load_index(body)
                self.assertEqual(bundle.assets['/'].body, body)
                self.assertIn('/assets/test.js', bundle.assets)
                self.assertIn('/assets/test.css', bundle.assets)

    def test_court_text_and_reference_paths_are_quarantined(self):
        target = self.root / 'public/assets/test.js'
        body = b'const forbidden = "Court of Owls";'
        target.write_bytes(body)
        changed = deepcopy(self.manifest)
        changed['files'][1].update(size=len(body), sha256=hashlib.sha256(body).hexdigest())
        with self.assertRaises(BridgeError): self.load(changed)
        changed['files'][1]['path'] = 'assets/talon.png'
        with self.assertRaises(BridgeError): self.load(changed)

    def test_bundle_id_cannot_choose_another_directory(self):
        for ident in ('../host-test', '.', '/tmp', 'C:\\private', 'host-test/extra'):
            with self.subTest(ident=ident), self.assertRaises(BridgeError):
                assets.load_bundle(self.app, ident, self.pin)

    def test_reparse_attribute_is_rejected_before_open(self):
        target = self.root / 'public/assets/test.js'
        self.assertIn('/assets/test.js', self.load().assets)  # Valid control.
        lstat, open_file = Path.lstat, Path.open
        opened = []
        class Reparse:
            def __init__(self, actual):
                self.actual = actual
                self.st_file_attributes = getattr(actual, 'st_file_attributes', 0) | stat.FILE_ATTRIBUTE_REPARSE_POINT
            def __getattr__(self, name):
                return getattr(self.actual, name)
        def target_lstat(path, *args, **kwargs):
            actual = lstat(path, *args, **kwargs)
            return Reparse(actual) if path == target else actual
        def observe_open(path, *args, **kwargs):
            if path == target: opened.append(path)
            return open_file(path, *args, **kwargs)
        with patch.object(Path, 'lstat', new=target_lstat), patch.object(Path, 'open', new=observe_open):
            with self.assertRaises(BridgeError): self.load()
        self.assertEqual(opened, [])
        self.assertIn('/assets/test.js', self.load().assets)

    def test_actual_file_symlink_is_rejected(self):
        target = self.root / 'public/assets/test.js'
        source = self.app / 'outside.js'
        source.write_bytes(target.read_bytes())
        target.unlink()
        try:
            target.symlink_to(source)
        except OSError as exc:
            self.skipTest('BLOCKED: OS does not permit creating a test symlink: ' + str(exc))
        with self.assertRaises(BridgeError): self.load()

    @unittest.skipUnless(os.name == 'nt', 'Windows junction acceptance')
    def test_actual_windows_junction_is_rejected(self):
        target = self.root / 'public/assets'
        moved = self.app / 'outside-assets'
        target.rename(moved)
        run = subprocess.run(['cmd', '/c', 'mklink', '/J', str(target), str(moved)],
                             capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        self.assertEqual(run.returncode, 0, run.stderr)
        with self.assertRaises(BridgeError): self.load()


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.now = 10.0
        self.bootstrap = Bootstrap('PRIVATE_CAPABILITY', clock=lambda: self.now)

    def test_issue_is_strong_random_and_single_use(self):
        before = random.getstate()
        first = self.bootstrap.issue()
        second = self.bootstrap.issue()
        self.assertEqual(len(second), 43)
        self.assertNotEqual(first, second)
        with self.assertRaises(BridgeError): self.bootstrap.redeem(first)
        self.assertEqual(self.bootstrap.redeem(second), 'PRIVATE_CAPABILITY')
        with self.assertRaises(BridgeError): self.bootstrap.redeem(second)
        self.assertEqual(random.getstate(), before)

    def test_expiry_is_monotonic_and_exact(self):
        code = self.bootstrap.issue()
        self.now += CODE_SECONDS
        with self.assertRaises(BridgeError) as caught: self.bootstrap.redeem(code)
        self.assertEqual(caught.exception.status, 401)

    def test_attempt_limit_does_not_reset_when_operator_reissues(self):
        code = self.bootstrap.issue()
        for _ in range(MAX_ATTEMPTS):
            with self.assertRaises(BridgeError) as caught: self.bootstrap.redeem('wrong')
            self.assertEqual(caught.exception.status, 401)
        code = self.bootstrap.issue()
        with self.assertRaises(BridgeError) as caught: self.bootstrap.redeem(code)
        self.assertEqual(caught.exception.status, 429)
        self.now += 60
        self.assertEqual(self.bootstrap.redeem(code), 'PRIVATE_CAPABILITY')

    def test_concurrent_redemption_has_exactly_one_winner(self):
        code = self.bootstrap.issue()
        def redeem(_):
            try: return self.bootstrap.redeem(code)
            except BridgeError as exc: return exc.status
        with ThreadPoolExecutor(max_workers=8) as pool: results = list(pool.map(redeem, range(8)))
        self.assertEqual(results.count('PRIVATE_CAPABILITY'), 1)
        self.assertEqual(results.count(401), 7)

    def test_close_revokes_and_rejects_new_codes(self):
        code = self.bootstrap.issue()
        self.bootstrap.close()
        with self.assertRaises(BridgeError): self.bootstrap.redeem(code)
        with self.assertRaises(BridgeError): self.bootstrap.issue()


class BrowserHostTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.app = Path(self.folder.name)
        root, manifest = fixture(self.app)
        self.bundle = assets.load_bundle(self.app, 'host-test', pin(root, manifest))
        self.checkpoint, self.config = self.app / 'career.json', self.app / 'host.json'
        with Bridge.create(self.checkpoint): pass
        self.host = BrowserHost.open(self.checkpoint, self.config, self.bundle)
        self.host.start()
        self.addCleanup(lambda: self.host.close())

    def headers(self, *, authorize=False):
        headers = {'Host': self.host.server.authority, 'Origin': self.host.server.origin,
                   'Content-Type': 'application/json'}
        if authorize: headers['Authorization'] = 'Bearer ' + self.host.server.capability
        return headers

    def call(self, path='/', method='GET', body=None, headers=None):
        conn = http.client.HTTPConnection('127.0.0.1', self.host.server.server_port, timeout=3)
        try:
            raw = json.dumps(body).encode() if isinstance(body, dict) else body
            conn.request(method, path, raw, self.headers() if headers is None else headers)
            response = conn.getresponse()
            data = response.read()
            result = json.loads(data) if data and response.getheader('Content-Type', '').startswith('application/json') else data
            return response.status, result, dict(response.getheaders())
        finally:
            conn.close()

    def redeem(self, code=None, **changes):
        request = dict(host_protocol_version=1, bundle_id=self.bundle.bundle_id,
                       code=self.host.server.bootstrap.issue() if code is None else code)
        request.update(changes)
        return self.call('/host/v1/bootstrap', 'POST', request)

    def command(self, request_id='wait-once', **changes):
        state = self.call('/api/v1/state', headers=self.headers(authorize=True))[1]
        request = dict(protocol_version=1, career_id=state['career_id'], lineage_id=state['lineage_id'],
                       request_id=request_id, expected_revision=state['revision'], command='wait', arguments={})
        request.update(changes)
        return request

    def test_assets_are_public_but_engine_and_session_are_not(self):
        before, rng = self.checkpoint.read_bytes(), random.getstate()
        for path in ('/', '/assets/test.js', '/assets/test.css'):
            status, body, headers = self.call(path)
            self.assertEqual(status, 200)
            self.assertNotIn(self.host.server.capability.encode(), body)
            self.assertEqual(headers['Cache-Control'], 'no-store')
            self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
            self.assertEqual(headers['Referrer-Policy'], 'no-referrer')
            self.assertEqual(headers['Cross-Origin-Resource-Policy'], 'same-origin')
            self.assertIn("connect-src 'self'", headers['Content-Security-Policy'])
            self.assertNotIn('unsafe-inline', headers['Content-Security-Policy'])
        for path in ('/api/v1/state', '/host/v1/session'):
            self.assertEqual(self.call(path)[0], 401)
        self.assertEqual(self.checkpoint.read_bytes(), before)
        self.assertEqual(random.getstate(), rng)

    def test_bootstrap_returns_only_process_capability_and_compatibility(self):
        before = self.checkpoint.read_bytes()
        code = self.host.server.bootstrap.issue()
        status, response, headers = self.redeem(code)
        self.assertEqual(status, 200)
        self.assertEqual(response['capability'], self.host.server.capability)
        self.assertEqual(response['bridge_protocol_version'], 1)
        self.assertEqual(response['mode'], 'local_engine')
        self.assertNotIn(code, json.dumps(response))
        self.assertNotIn('world', response)
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertNotIn('Access-Control-Allow-Origin', headers)
        self.assertEqual(self.redeem(code)[0], 401)
        self.assertEqual(self.checkpoint.read_bytes(), before)

    def test_bootstrap_has_no_http_logs_or_hidden_state(self):
        code = self.host.server.bootstrap.issue()
        out, err = io.StringIO(), io.StringIO()
        with patch('sys.stdout', out), patch('sys.stderr', err):
            status, response, _ = self.redeem(code)
            self.assertEqual(self.call('/host/v1/session', headers=self.headers(authorize=True))[0], 200)
        self.assertEqual(status, 200)
        self.assertEqual(out.getvalue(), '')
        self.assertEqual(err.getvalue(), '')
        self.assertEqual(set(response), {'host_protocol_version', 'bridge_protocol_version', 'bundle_id',
                                       'manifest_sha256', 'engine_release', 'instance_id', 'mode',
                                       'session_lifetime', 'capability'})

    def test_parallel_http_redemption_consumes_one_code(self):
        code = self.host.server.bootstrap.issue()
        with ThreadPoolExecutor(max_workers=4) as pool:
            statuses = list(pool.map(lambda _: self.redeem(code)[0], range(4)))
        self.assertEqual(sorted(statuses), [200, 401, 401, 401])
        self.assertEqual(self.host.bridge.state()['revision'], 0)

    def test_bad_origins_hosts_and_csrf_do_not_consume_code(self):
        code = self.host.server.bootstrap.issue()
        body = dict(host_protocol_version=1, bundle_id='host-test', code=code)
        cases = [('Host', 'attacker.example'), ('Host', 'localhost:' + str(self.host.server.server_port)),
                 ('Origin', 'https://evil.example'), ('Origin', 'null'), ('Sec-Fetch-Site', 'cross-site')]
        before, rng = self.checkpoint.read_bytes(), random.getstate()
        for key, value in cases:
            with self.subTest(header=key, value=value):
                headers = self.headers()
                headers[key] = value
                self.assertEqual(self.call('/host/v1/bootstrap', 'POST', body, headers)[0], 403)
                self.assertEqual(self.call('/', headers=headers)[0], 403)
        headers = self.headers()
        del headers['Origin']
        self.assertEqual(self.call('/host/v1/bootstrap', 'POST', body, headers)[0], 403)
        self.assertEqual(self.redeem(code)[0], 200)
        self.assertEqual(self.checkpoint.read_bytes(), before)
        self.assertEqual(random.getstate(), rng)

    def test_expired_wrong_and_rate_limited_codes(self):
        bootstrap = Bootstrap(self.host.server.capability, clock=lambda: 10)
        self.host.server.bootstrap = bootstrap
        code = bootstrap.issue()
        bootstrap._clock = lambda: 130
        self.assertEqual(self.redeem(code)[0], 401)
        for _ in range(MAX_ATTEMPTS - 1): self.assertEqual(self.redeem('wrong')[0], 401)
        self.assertEqual(self.redeem('wrong')[0], 429)

    def test_bootstrap_schema_bundle_version_json_and_size_are_strict(self):
        code = self.host.server.bootstrap.issue()
        for changes in ({'bundle_id': 'old'}, {'host_protocol_version': True},
                        {'host_protocol_version': 2}, {'extra': 'field'}):
            self.assertEqual(self.redeem(code, **changes)[0], 409)
        self.assertEqual(self.call('/host/v1/bootstrap', 'POST', b'x' * 1025)[0], 413)
        self.assertEqual(self.call('/host/v1/bootstrap', 'POST', b'{"code":1,"code":2}')[0], 400)
        headers = self.headers()
        headers['Content-Type'] = 'text/plain'
        self.assertEqual(self.call('/host/v1/bootstrap', 'POST', b'{}', headers)[0], 415)
        self.assertEqual(self.redeem(code)[0], 200)

    def test_duplicate_bootstrap_security_headers_are_rejected(self):
        code = self.host.server.bootstrap.issue()
        for duplicate in ('Host', 'Origin', 'Content-Length'):
            with self.subTest(duplicate=duplicate):
                conn = http.client.HTTPConnection('127.0.0.1', self.host.server.server_port, timeout=3)
                try:
                    conn.putrequest('POST', '/host/v1/bootstrap', skip_host=True)
                    for key, value in dict(self.headers(), **{'Content-Length': '2'}).items():
                        conn.putheader(key, value)
                        if key == duplicate: conn.putheader(key, value)
                    conn.endheaders(b'{}')
                    response = conn.getresponse()
                    self.assertEqual(response.status, 400)
                    self.assertEqual(json.loads(response.read())['error']['code'], 'INVALID_HEADERS')
                finally: conn.close()
        self.assertEqual(self.redeem(code)[0], 200)

    def test_no_traversal_fallback_source_saves_or_court_paths(self):
        for path in ('/index.html', '/manifest.json', '/unknown/spa', '/assets/../index.html', '/assets/%2e%2e/index.html',
                     '/assets/%252e%252e/index.html', '/assets/test.js:secret', '/assets/test.js.map',
                     '/assets\\test.js', '/C:/Windows/file', '/docs/GOON_MASTER_ROSTER.md', '/career.json',
                     '/bridge_http.py', '/source.zip', '/content/images-references/Goon%20Life%2047%20owls.jpg',
                     '/?mode=live', '/assets/test.js?v=1', '/host/v2/session'):
            with self.subTest(path=path): self.assertEqual(self.call(path)[0], 404)

    def test_methods_and_parser_errors_do_not_gain_authority(self):
        before = self.checkpoint.read_bytes()
        for method in ('TRACE', 'CONNECT', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'UNKNOWN', 'HEAD'):
            self.assertEqual(self.call(method=method)[0], 401)
            status, body, headers = self.call(method=method, headers=self.headers(authorize=True))
            self.assertEqual(status, 405)
            self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(self.call('/host/v1/bootstrap')[0], 405)
        self.assertEqual(self.call('/host/v1/session', 'POST', {}, self.headers(authorize=True))[0], 405)
        self.assertEqual(self.checkpoint.read_bytes(), before)

    def test_api_duplicate_wait_and_conflicting_reuse_keep_existing_semantics(self):
        request = self.command()
        first = self.call('/api/v1/commands', 'POST', request, self.headers(authorize=True))[1]
        duplicate = self.call('/api/v1/commands', 'POST', request, self.headers(authorize=True))[1]
        self.assertEqual(first['receipt'], duplicate['receipt'])
        self.assertTrue(duplicate['duplicate'])
        self.assertEqual(duplicate['state']['day'], 1)
        changed = dict(request, command='settle_in')
        status, response, _ = self.call('/api/v1/commands', 'POST', changed, self.headers(authorize=True))
        self.assertEqual(status, 409)
        self.assertEqual(response['error']['code'], 'REQUEST_ID_REUSED')
        self.assertNotIn('events', first)

    def test_parallel_tabs_at_one_revision_have_one_effect(self):
        request = self.command()
        requests = [request, dict(request, request_id='other-tab')]
        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = list(pool.map(lambda r: self.call('/api/v1/commands', 'POST', r,
                                                       self.headers(authorize=True))[0], requests))
        self.assertEqual(sorted(statuses), [200, 409])
        self.assertEqual(self.host.bridge.state()['state']['day'], 1)

    def test_reload_and_host_restart_preserve_operation_and_port(self):
        request = self.command()
        first = self.call('/api/v1/commands', 'POST', request, self.headers(authorize=True))[1]
        port, old_cap = self.host.server.server_port, self.host.server.capability
        identity = first['career_id'], first['lineage_id']
        # Reload simulation is another authenticated HTTP connection, not a browser test.
        self.assertEqual(self.call('/host/v1/session', headers=self.headers(authorize=True))[0], 200)
        self.host.close()
        self.host = BrowserHost.open(self.checkpoint, self.config, self.bundle)
        self.host.start()
        self.assertEqual(self.host.server.server_port, port)
        self.assertNotEqual(self.host.server.capability, old_cap)
        self.assertEqual(self.call('/api/v1/state', headers=dict(self.headers(), Authorization='Bearer ' + old_cap))[0], 401)
        self.assertEqual(self.redeem()[0], 200)
        status, recovered, _ = self.call('/api/v1/operations/wait-once', headers=self.headers(authorize=True))
        self.assertEqual(status, 200)
        self.assertEqual(recovered['receipt'], first['receipt'])
        self.assertEqual((recovered['career_id'], recovered['lineage_id']), identity)
        self.assertEqual(self.call('/api/v1/commands', 'POST', request, self.headers(authorize=True))[1]['state']['day'], 1)

    def test_real_tess_shift_matches_direct_engine_with_quoted_arguments(self):
        self.assertEqual(self.redeem()[0], 200)
        direct = engine.create_career(42)
        def send(command, **args):
            request = self.command(request_id='step-' + str(self.host.bridge.state()['revision']),
                                   command=command, arguments=args)
            status, response, _ = self.call('/api/v1/commands', 'POST', request, self.headers(authorize=True))
            self.assertEqual(status, 200, response)
            engine.execute_command(direct, command, **args)
            self.assertEqual(decode_json(self.checkpoint.read_text())['world'], direct)
            return response
        send('settle_in')
        send('wait')
        status, quote, _ = self.call('/api/v1/travel-quotes', 'POST',
                                    dict(protocol_version=1, destination='p032', mode='walk'),
                                    self.headers(authorize=True))
        self.assertEqual(status, 200)
        # Quotes use canonical IDs. The historical frozen replay used the p032
        # alias, so its recorded command arguments (and world hash) differ.
        self.assertEqual(quote['quote']['arguments']['destination'], 'goon.poi.p032')
        send(quote['quote']['command'], **quote['quote']['arguments'])
        response = send('choose', choice_id='goon.choice.0.opening_shift', option_id='work')
        state = response['state']
        self.assertEqual((state['player']['cash'], state['budgets']['actions_remaining'],
                          state['budgets']['travel_units_remaining']), (60, 2, 17))
        self.assertEqual(next(c for c in state['contacts'] if c['id'] == 'goon.contact.tess')['standing'], 1)
        world = decode_json(self.checkpoint.read_text())['world']
        from bridge_checkpoint import digest
        self.assertEqual(digest(world), '61c395ac64c42ac603a5dddf24010db343db2c8620e5654c8122707639645718')

    def test_actual_process_restart_recovers_a_lost_ack_on_same_port(self):
        self.host.close()
        code = '''
import json,os,sys
from bridge_assets import load_bundle
from browser_host import BrowserHost
bundle=load_bundle(sys.argv[1],'host-test',sys.argv[4])
with BrowserHost.open(sys.argv[2],sys.argv[3],bundle) as host:
    host.start()
    print(json.dumps(dict(port=host.server.server_port,code=host.server.bootstrap.issue())),flush=True)
    if input()=='crash': os._exit(71)
'''
        processes = []
        def launch():
            process = subprocess.Popen([sys.executable, '-B', '-c', code, str(self.app), str(self.checkpoint),
                                        str(self.config), self.bundle.manifest_sha256], cwd=Path(__file__).resolve().parents[1],
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            processes.append(process)
            # A failed child exits and closes stdout; a successful one emits once.
            return process, json.loads(process.stdout.readline())
        def call(port, path, method='GET', body=None, capability=None):
            conn = http.client.HTTPConnection('127.0.0.1', port, timeout=3)
            headers = dict(Host=f'127.0.0.1:{port}', Origin=f'http://127.0.0.1:{port}', **{'Content-Type':'application/json'})
            if capability: headers['Authorization'] = 'Bearer ' + capability
            try:
                conn.request(method, path, json.dumps(body) if body is not None else None, headers)
                response = conn.getresponse()
                return response.status, json.loads(response.read())
            finally: conn.close()
        try:
            process, launch_state = launch()
            port = launch_state['port']
            status, auth = call(port, '/host/v1/bootstrap', 'POST',
                                dict(host_protocol_version=1, bundle_id='host-test', code=launch_state['code']))
            self.assertEqual(status, 200)
            capability = auth['capability']
            state = call(port, '/api/v1/state', capability=capability)[1]
            request = dict(protocol_version=1, career_id=state['career_id'], lineage_id=state['lineage_id'],
                           expected_revision=0, request_id='lost-in-process', command='wait', arguments={})
            conn = http.client.HTTPConnection('127.0.0.1', port, timeout=3)
            conn.request('POST', '/api/v1/commands', json.dumps(request),
                         dict(Host=f'127.0.0.1:{port}', Origin=f'http://127.0.0.1:{port}',
                              Authorization='Bearer '+capability, **{'Content-Type':'application/json'}))
            conn.close()  # Never read the command acknowledgment.
            deadline = time.monotonic() + 5
            while True:
                receipt = call(port, '/api/v1/operations/lost-in-process', capability=capability)[1]
                if receipt['operation_status'] == 'committed': break
                self.assertLess(time.monotonic(), deadline)
                time.sleep(0.01)
            process.communicate('crash\n', timeout=10)
            self.assertEqual(process.returncode, 71)
            process, resumed = launch()
            self.assertEqual(resumed['port'], port)
            self.assertEqual(call(port, '/api/v1/state', capability=capability)[0], 401)
            auth = call(port, '/host/v1/bootstrap', 'POST',
                        dict(host_protocol_version=1, bundle_id='host-test', code=resumed['code']))[1]
            duplicate = call(port, '/api/v1/commands', 'POST', request, auth['capability'])[1]
            self.assertTrue(duplicate['duplicate'])
            self.assertEqual(duplicate['receipt'], receipt['receipt'])
            self.assertEqual(duplicate['state']['day'], 1)
            process.communicate('quit\n', timeout=10)
            self.assertEqual(process.returncode, 0)
        finally:
            for process in processes:
                if process.poll() is None: process.kill()
                process.communicate(timeout=10)

    def test_port_collision_never_changes_config_or_checkpoint(self):
        before, config = self.checkpoint.read_bytes(), self.config.read_bytes()
        with self.assertRaises(OSError): BrowserHost.open(self.checkpoint, self.config, self.bundle)
        with self.assertRaises(OSError): BrowserServer(None, self.bundle, self.host.server.server_port)
        # A listener using the old headless SO_REUSEADDR policy cannot join it.
        with self.assertRaises(OSError): BridgeServer(None, self.host.server.server_port)
        self.assertEqual(self.checkpoint.read_bytes(), before)
        self.assertEqual(self.config.read_bytes(), config)

    def test_invalid_config_does_not_choose_a_new_port(self):
        self.host.close()
        for config in ({'host_config_version': 1, 'port': 0}, {'host_config_version': True, 'port': 1234},
                       {'host_config_version': 1, 'port': True}, {'host_config_version': 2, 'port': 1234}):
            self.config.write_text(json.dumps(config))
            with self.subTest(config=config), self.assertRaises(ValueError):
                BrowserHost.open(self.checkpoint, self.config, self.bundle)

    def test_configuration_cannot_alias_career_storage(self):
        for path in (self.checkpoint, Path(str(self.checkpoint) + '.bak'), Path(str(self.checkpoint) + '.lock')):
            with self.subTest(path=path), self.assertRaises(BridgeError):
                BrowserHost.open(self.checkpoint, path, self.bundle)

    def test_missing_or_locked_engine_never_creates_a_career(self):
        missing = self.app / 'missing.json'
        with self.assertRaises(OSError): BrowserHost.open(missing, self.app / 'missing-host.json', self.bundle)
        self.assertFalse(missing.exists())
        with self.assertRaises(BridgeError):
            BrowserHost.open(self.checkpoint, self.app / 'other-host.json', self.bundle)

    def test_historical_files_require_explicit_bridge_import(self):
        source = Path(__file__).resolve().parent / 'fixtures/m010.json'
        raw = self.app / 'legacy.json'
        raw.write_bytes(source.read_bytes())
        before = raw.read_bytes()
        with self.assertRaises(BridgeError):
            BrowserHost.open(raw, self.app / 'legacy-host.json', self.bundle)
        self.assertEqual(raw.read_bytes(), before)
        target = self.app / 'imported.json'
        with Bridge.import_legacy(raw, target): pass
        imported_before = target.read_bytes()
        with BrowserHost.open(target, self.app / 'imported-host.json', self.bundle) as host:
            state = host.bridge.state()['state']
            self.assertEqual(state['systems']['daily_life'], 'not_adopted')
            self.assertEqual(state['systems']['navigation'], 'not_adopted')
        self.assertEqual(target.read_bytes(), imported_before)
        self.assertEqual(raw.read_bytes(), before)

    def test_config_publication_failure_releases_listener_and_preserves_career(self):
        self.host.close()
        before = self.checkpoint.read_bytes()
        config = self.app / 'new-config.json'
        with patch('browser_host._publish_config', side_effect=OSError('injected')), self.assertRaises(OSError):
            BrowserHost.open(self.checkpoint, config, self.bundle)
        self.assertEqual(self.checkpoint.read_bytes(), before)
        with BrowserHost.open(self.checkpoint, config, self.bundle): pass

    def test_late_startup_failure_releases_the_opened_career(self):
        self.host.close()
        from bridge_checkpoint import CareerLock
        def faulty_config_lock(path):
            lock = CareerLock(path)
            close = lock.close
            def close_then_fail():
                close()
                raise OSError('injected configuration-lock cleanup failure')
            lock.close = close_then_fail
            return lock
        with patch('browser_host.CareerLock', side_effect=faulty_config_lock), self.assertRaises(OSError):
            BrowserHost.open(self.checkpoint, self.config, self.bundle)
        with Bridge.open(self.checkpoint) as bridge:
            self.assertEqual(bridge.state()['revision'], 0)

    def test_cli_missing_bundle_fails_before_touching_engine_or_browser(self):
        args = ['browser_host.py', '--checkpoint', str(self.app / 'absent.json'), '--bundle-id', 'absent',
                '--manifest-sha256', '0' * 64]
        with patch.object(sys, 'argv', args), patch('browser_host.Bridge.open') as opened, \
                patch('browser_host.webbrowser.open') as browser, patch('sys.stderr', io.StringIO()):
            with self.assertRaises(SystemExit): main()
        opened.assert_not_called()
        browser.assert_not_called()

    def test_cli_opens_secret_free_url_and_can_reauthorize_then_quit(self):
        args = ['browser_host.py', '--checkpoint', str(self.checkpoint), '--bundle-id', 'host-test',
                '--manifest-sha256', self.bundle.manifest_sha256, '--host-config', str(self.config)]
        before = self.checkpoint.read_bytes()
        self.host.close()
        output = io.StringIO()
        with patch.object(sys, 'argv', args), patch('browser_host.load_bundle', return_value=self.bundle), \
                patch('browser_host.webbrowser.open') as browser, patch('builtins.input', side_effect=['', 'quit']), \
                patch('sys.stdout', output):
            main()
        url = browser.call_args.args[0]
        self.assertRegex(url, r'^http://127\.0\.0\.1:[0-9]+/$')
        self.assertEqual(output.getvalue().count('One-time authorization code'), 2)
        self.assertNotIn('Session capability', output.getvalue())
        self.assertEqual(self.checkpoint.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
