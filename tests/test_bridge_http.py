"""Actual loopback requests: authentication, parser limits and durable recovery."""
from concurrent.futures import ThreadPoolExecutor
import http.client
import json
from pathlib import Path
import random
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import bridge_checkpoint as disk
from bridge_http import BridgeServer, MAX_REQUEST_BYTES
from engine_bridge import Bridge


class BridgeHTTPTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name) / 'checkpoint.json'
        self.bridge = Bridge.create(self.path)
        self.server = BridgeServer(self.bridge)
        self.thread = threading.Thread(target=lambda: self.server.serve_forever(poll_interval=0.01), daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        self.bridge.close()
        self.folder.cleanup()

    def headers(self):
        return {'Host': self.server.authority, 'Origin': self.server.origin,
                'Authorization': 'Bearer ' + self.server.capability, 'Content-Type': 'application/json'}

    def call(self, method='GET', path='/api/v1/state', body=None, headers=None):
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        try:
            data = json.dumps(body).encode() if isinstance(body, (dict, list)) else body
            conn.request(method, path, body=data, headers=self.headers() if headers is None else headers)
            response = conn.getresponse()
            raw = response.read()
            return response.status, json.loads(raw) if raw else None, dict(response.getheaders())
        finally:
            conn.close()

    def request(self, command='wait', **args):
        state = self.call()[1]
        return dict(protocol_version=1, career_id=state['career_id'], lineage_id=state['lineage_id'],
                    request_id=f'request-{state["revision"]}', expected_revision=state['revision'],
                    command=command, arguments=args)

    def send(self, command, **args):
        status, result, _ = self.call('POST', '/api/v1/commands', self.request(command, **args))
        self.assertEqual(status, 200, result)
        return result

    def test_loopback_state_is_safe_and_not_cached(self):
        self.assertEqual(self.server.server_address[0], '127.0.0.1')
        status, state, headers = self.call()
        self.assertEqual(status, 200)
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertNotIn('Access-Control-Allow-Origin', headers)
        self.assertNotIn(self.server.capability, json.dumps(state))
        self.assertNotIn('world', state)
        self.assertNotIn('events', state)
        self.assertEqual(state['state']['budgets']['daily_actions'], 3)
        self.assertEqual(state['state']['budgets']['daily_travel_units'], 18)
        # Same-origin GET may omit Origin, but still requires the capability.
        headers = self.headers()
        del headers['Origin']
        self.assertEqual(self.call(headers=headers)[0], 200)

    def test_unsafe_hosts_origins_and_capabilities_never_mutate(self):
        before, rng = self.path.read_bytes(), random.getstate()
        request = self.request()
        cases = [('Host', 'evil.example', 403), ('Host', 'localhost:' + str(self.server.server_port), 403),
                 ('Origin', 'https://evil.example', 403), ('Origin', 'null', 403),
                 ('Authorization', 'Bearer wrong', 401), ('Authorization', '\u00e9', 401),
                 ('Sec-Fetch-Site', 'cross-site', 403)]
        for key, value, expected in cases:
            with self.subTest(key=key, value=value):
                headers = self.headers()
                headers[key] = value
                self.assertEqual(self.call('POST', '/api/v1/commands', request, headers)[0], expected)
        for key, status in [('Authorization', 401), ('Origin', 403)]:
            headers = self.headers()
            del headers[key]
            self.assertEqual(self.call('POST', '/api/v1/commands', request, headers)[0], status)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(random.getstate(), rng)

    def test_payload_limit_content_type_and_transfer_encoding(self):
        request = self.request()
        before = self.path.read_bytes()
        cases = [('Content-Length', str(MAX_REQUEST_BYTES + 1), 413),
                 ('Content-Length', '-1', 400), ('Content-Length', 'x', 400),
                 ('Content-Type', 'text/plain', 415), ('Transfer-Encoding', 'chunked', 400)]
        for key, value, expected in cases:
            with self.subTest(key=key):
                headers = self.headers()
                headers[key] = value
                self.assertEqual(self.call('POST', '/api/v1/commands', request, headers)[0], expected)
        self.assertEqual(self.path.read_bytes(), before)

    def test_duplicate_security_headers_are_rejected(self):
        for duplicate in ('Host', 'Origin', 'Authorization', 'Content-Length'):
            with self.subTest(header=duplicate):
                conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
                try:
                    conn.putrequest('POST', '/api/v1/commands', skip_host=True)
                    headers = dict(self.headers(), **{'Content-Length': '2'})
                    for name, value in headers.items():
                        conn.putheader(name, value)
                        if name == duplicate:
                            conn.putheader(name, value)
                    conn.endheaders(b'{}')
                    response = conn.getresponse()
                    self.assertEqual(response.status, 400)
                    self.assertEqual(json.loads(response.read())['error']['code'], 'INVALID_HEADERS')
                finally:
                    conn.close()

    def test_malformed_json_wrong_versions_and_forged_fields(self):
        before = self.path.read_bytes()
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e999}', b'null', b'\xff', b'{'):
            with self.subTest(raw=raw):
                self.assertEqual(self.call('POST', '/api/v1/commands', raw)[0], 400)
        for field in ('cash', 'cost', 'location', 'snapshot'):
            request = self.request()
            request['arguments'][field] = '999'
            self.assertEqual(self.call('POST', '/api/v1/commands', request)[0], 400)
        request = self.request()
        request['protocol_version'] = 2
        self.assertEqual(self.call('POST', '/api/v1/commands', request)[0], 409)
        self.assertEqual(self.path.read_bytes(), before)

    def test_arbitrary_files_debug_queries_and_unsupported_routes_are_absent(self):
        for path in ('/', '/snapshot', '/api/v1/snapshot', '/api/v1/state?developer=true',
                     '/../checkpoint.json', '/api/v2/state', '/game_service.py', '/docs/README.md'):
            with self.subTest(path=path):
                self.assertEqual(self.call(path=path)[0], 404)
        self.assertEqual(self.call('GET', '/api/v1/operations/../../checkpoint.json')[0], 400)
        self.assertEqual(self.call('POST', '/api/v1/load', {'path': str(self.path)})[0], 404)
        self.assertEqual(self.call('OPTIONS')[0], 405)

    def test_quote_is_observational_and_repair_is_real(self):
        self.send('settle_in')
        self.send('wait')
        before = self.path.read_bytes()
        status, quote, _ = self.call('POST', '/api/v1/travel-quotes',
                                    dict(protocol_version=1, destination='p032', mode='walk'))
        self.assertEqual(status, 200)
        self.assertEqual(quote['quote']['cost'], 1)
        self.assertEqual(self.path.read_bytes(), before)
        self.send(quote['quote']['command'], **quote['quote']['arguments'])
        result = self.send('choose', choice_id='goon.choice.0.opening_shift', option_id='work')
        self.assertEqual(result['state']['player']['cash'], 60)
        tess = next(c for c in result['state']['contacts'] if c['id'] == 'goon.contact.tess')
        self.assertEqual(tess['standing'], 1)
        recovery = self.call(path='/api/v1/operations/' + result['receipt']['request_id'])[1]
        self.assertEqual(recovery['receipt'], result['receipt'])
        self.assertEqual(result['state']['budgets']['actions_remaining'], 2)

    def test_stale_competing_intents_are_serialized(self):
        first = self.request()
        second = dict(first, request_id='competing')
        def submit(request):
            return self.call('POST', '/api/v1/commands', request)[0]
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(submit, [first, second]))
        self.assertEqual(sorted(results), [200, 409])
        self.assertEqual(self.call()[1]['state']['day'], 1)

    def test_lost_http_ack_is_recovered_without_another_wait(self):
        request = self.request()
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        conn.request('POST', '/api/v1/commands', body=json.dumps(request), headers=self.headers())
        conn.close()  # Deliberately never read the acknowledgment.
        deadline = time.monotonic() + 3
        while True:
            recovered = self.call(path='/api/v1/operations/' + request['request_id'])[1]
            if recovered['operation_status'] == 'committed':
                break
            self.assertLess(time.monotonic(), deadline)
            time.sleep(0.01)
        duplicate = self.call('POST', '/api/v1/commands', request)[1]
        self.assertEqual(duplicate['receipt'], recovered['receipt'])
        self.assertEqual(duplicate['state']['day'], 1)

    def test_uncertain_publication_uses_operation_recovery(self):
        request = self.request()
        replace = disk.os.replace
        def fail_after(source, target):
            replace(source, target)
            if Path(target) == self.path:
                raise OSError('PRIVATE_FILESYSTEM_DETAILS')
        with patch('bridge_checkpoint.os.replace', side_effect=fail_after):
            status, result, _ = self.call('POST', '/api/v1/commands', request)
        self.assertEqual(status, 503)
        self.assertEqual(result['error']['code'], 'OUTCOME_UNKNOWN')
        self.assertNotIn('PRIVATE_FILESYSTEM_DETAILS', json.dumps(result))
        self.assertEqual(self.call('POST', '/api/v1/commands', request)[0], 503)
        recovered = self.call(path='/api/v1/operations/' + request['request_id'])[1]
        self.assertEqual(recovered['state']['day'], 1)
        self.assertEqual(self.call('POST', '/api/v1/commands', request)[1]['receipt'], recovered['receipt'])

    def test_restart_rotates_capability_but_preserves_operation_identity(self):
        request = self.request()
        original = self.call('POST', '/api/v1/commands', request)[1]
        old_capability = self.server.capability
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        self.bridge.close()
        self.bridge = Bridge.open(self.path)
        self.server = BridgeServer(self.bridge)
        self.thread = threading.Thread(target=lambda: self.server.serve_forever(poll_interval=0.01), daemon=True)
        self.thread.start()
        headers = self.headers()
        headers['Authorization'] = 'Bearer ' + old_capability
        self.assertEqual(self.call(headers=headers)[0], 401)
        duplicate = self.call('POST', '/api/v1/commands', request)[1]
        self.assertEqual(duplicate['receipt'], original['receipt'])
        self.assertTrue(duplicate['duplicate'])
        self.assertEqual(duplicate['state']['day'], 1)


if __name__ == '__main__':
    unittest.main()
