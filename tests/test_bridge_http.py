"""Actual loopback requests: authentication, parser limits and durable recovery."""
from concurrent.futures import ThreadPoolExecutor
import http.client
import json
from pathlib import Path
import random
import socket
import struct
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import bridge_checkpoint as disk
from bridge_http import BridgeServer, Handler, MAX_REQUEST_BYTES
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

    def raw_call(self, headers, chunks=(), *, allow_termination=False):
        """Use actual bytes: HTTPConnection otherwise invents missing framing."""
        with socket.create_connection(('127.0.0.1', self.server.server_port), timeout=2) as conn:
            packet = 'POST /api/v1/commands HTTP/1.1\r\n' + ''.join(
                f'{k}: {v}\r\n' for k, v in headers.items()) + '\r\n'
            try:
                conn.sendall(packet.encode('ascii'))
                for delay, chunk in chunks:
                    if delay:
                        time.sleep(delay)
                    conn.sendall(chunk)
                conn.shutdown(socket.SHUT_WR)
                with http.client.HTTPResponse(conn) as response:
                    response.begin()
                    return response.status, json.loads(response.read())
            except (ConnectionError, http.client.RemoteDisconnected):
                if not allow_termination:
                    raise
                return None  # Only deliberately malformed/excessive framing permits this.

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

    def test_housing_wire_shapes_preserve_v1_command_and_operation_envelopes(self):
        fresh = self.call()[1]
        current_path = '/api/v1/housing'
        status, current, headers = self.call(path=current_path)
        self.assertEqual(status, 200)
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertNotIn('Access-Control-Allow-Origin', headers)
        self.assertEqual(current, dict(protocol_version=1, career_id=fresh['career_id'],
                                       lineage_id=fresh['lineage_id'], revision=0,
                                       pay_room='not_adopted', latest_settlement=None))
        self.send('settle_in')
        self.assertEqual(self.call(path=current_path)[1]['pay_room'], 'pending')
        self.send('wait')
        self.assertEqual(self.call(path=current_path)[1]['pay_room'], 'eligible')
        paid = self.send('pay_room')
        ident = paid['receipt']['request_id']
        prefix = '/api/v1/housing/operations/'
        old_operation = '/api/v1/operations/' + ident
        old = self.call(path=old_operation)[1]
        self.assertEqual(set(paid), {'protocol_version', 'career_id', 'lineage_id', 'revision',
                                     'allowed_commands', 'receipt', 'duplicate', 'state'})
        self.assertEqual(set(paid['receipt']), {'request_id', 'revision', 'command_sequence',
                                               'command', 'day', 'status'})
        self.assertEqual(set(paid['state']['housing']), {'status', 'home_id', 'next_due_day', 'arrears', 'prepaid'})
        self.assertEqual(old, dict(paid, operation_status='committed'))
        expected = dict(day=1, kind='prepay', paid=30, credit_applied=0,
                        balance_after=dict(cash='10', arrears=0, prepaid=30, next_due_day=7))
        before = self.path.read_bytes()
        backup = Path(str(self.path) + '.bak')
        old_backup = backup.read_bytes()
        for path in (current_path, prefix + ident):
            status, data, headers = self.call(path=path)
            self.assertEqual(status, 200)
            self.assertEqual(headers['Cache-Control'], 'no-store')
            self.assertNotIn('Access-Control-Allow-Origin', headers)
            settlement = data['latest_settlement'] if path == current_path else data['settlements'][0]
            self.assertEqual(settlement, expected)
            for integer in ('day', 'paid', 'credit_applied'):
                self.assertIs(type(settlement[integer]), int)
            for integer in ('arrears', 'prepaid', 'next_due_day'):
                self.assertIs(type(settlement['balance_after'][integer]), int)
            self.assertRegex(settlement['balance_after']['cash'], r'^(0|[1-9][0-9]*)$')
            if path == current_path:
                self.assertEqual(data, dict(current, revision=3, pay_room='no_payable_balance',
                                            latest_settlement=expected))
            else:
                self.assertEqual(data, dict(protocol_version=1, career_id=paid['career_id'],
                                            lineage_id=paid['lineage_id'], revision=3,
                                            receipt=paid['receipt'], settlements=[expected]))
        self.assertEqual(self.call(path=old_operation)[1], old)
        status, response, _ = self.call(path=prefix + 'never-submitted')
        self.assertEqual((status, response['error']['code']), (404, 'NOT_FOUND'))
        self.assertEqual(self.call(path='/api/v1/operations/never-submitted')[1]['operation_status'], 'not_found')
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(backup.read_bytes(), old_backup)

    def test_housing_rejects_unauthorized_and_noncanonical_reads_without_writing(self):
        self.send('settle_in')
        wait = self.send('wait')
        paths = ('/api/v1/housing', '/api/v1/housing/operations/' + wait['receipt']['request_id'])
        before = self.path.read_bytes()
        backup = Path(str(self.path) + '.bak')
        old_backup = backup.read_bytes()
        for path in paths:
            for key, value, status in (('Authorization', None, 401), ('Authorization', 'Bearer wrong', 401),
                                       ('Origin', 'https://evil.example', 403), ('Host', 'evil.example', 403)):
                with self.subTest(path=path, key=key, value=value):
                    headers = self.headers()
                    if value is None:
                        del headers[key]
                    else:
                        headers[key] = value
                    self.assertEqual(self.call(path=path, headers=headers)[0], status)
            for alias in (path + '?', path + '#', path + '?ignored=1', '/' + path, path + '/'):
                with self.subTest(path=alias):
                    self.assertEqual(self.call(path=alias)[0], 404)
            self.assertEqual(self.call(path=path, body=b'{}')[0], 400)
            self.assertEqual(self.call('PUT', path)[0], 405)
            self.assertEqual(self.call('POST', path, {})[0], 404)
        status, response, _ = self.call(path='/api/v1/housing/operations/%72equest-1')
        self.assertEqual((status, response['error']['code']), (400, 'INVALID_REQUEST'))
        self.assertEqual(self.call(path='/api/v1/housing/operations/')[0], 404)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(backup.read_bytes(), old_backup)

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
            with self.subTest(key=key, value=value):
                headers = self.headers()
                headers[key] = value
                self.assertEqual(self.call('POST', '/api/v1/commands', request, headers)[0], expected)
        self.assertEqual(self.path.read_bytes(), before)

    def test_missing_invalid_and_oversized_lengths_never_execute(self):
        before, state, rng = self.path.read_bytes(), self.bridge.state(), random.getstate()
        body = json.dumps(self.request()).encode()
        for value, status in ((None, 400), ('x', 400), ('-1', 400), ('16385', 413)):
            with self.subTest(length=value):
                headers = self.headers()
                if value is not None:
                    headers['Content-Length'] = value
                # A whole valid command deliberately paired with invalid framing.
                result = self.raw_call(headers, [(0, body)], allow_termination=True)
                if result is not None:
                    self.assertEqual(result[0], status)
        # A complete, accurately framed policy rejection must be readable.
        headers = dict(self.headers(), **{'Content-Length': '16385'})
        self.assertEqual(self.raw_call(headers, [(0, b'x' * 16385)])[0], 413)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.bridge.state(), state)
        self.assertEqual(random.getstate(), rng)

    def test_extra_bytes_after_invalid_json_are_never_processed(self):
        before, rng = self.path.read_bytes(), random.getstate()
        headers = dict(self.headers(), **{'Content-Length': '2'})
        # Only the first two bytes belong to the body; excess bytes must not be
        # reinterpreted as another command, or drained without a fixed bound.
        result = self.raw_call(headers, [(0, b'{{' + b'x' * (MAX_REQUEST_BYTES * 4))],
                               allow_termination=True)
        if result is not None:
            self.assertEqual(result[0], 400)
            self.assertEqual(result[1]['error']['code'], 'MALFORMED_JSON')
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(random.getstate(), rng)

    def test_trailing_bytes_cannot_execute_a_second_framed_command(self):
        request = self.request()
        body = json.dumps(request).encode()
        headers = dict(self.headers(), **{'Content-Length': str(len(body))})
        second = json.dumps(dict(request, request_id='second-wait', expected_revision=1)).encode()
        packet = (f'POST /api/v1/commands HTTP/1.1\r\nHost: {self.server.authority}\r\n'
                  f'Authorization: Bearer {self.server.capability}\r\n'
                  f'Origin: {self.server.origin}\r\nContent-Type: application/json\r\n'
                  f'Content-Length: {len(second)}\r\n\r\n').encode() + second
        # A valid declared body is one request, even if a peer sends more bytes.
        self.raw_call(headers, [(0, body + packet + b'x' * (MAX_REQUEST_BYTES * 4))],
                      allow_termination=True)
        duplicate = self.call('POST', '/api/v1/commands', request)[1]
        self.assertTrue(duplicate['duplicate'])
        self.assertEqual(duplicate['state']['day'], 1)
        self.assertEqual(duplicate['revision'], 1)

    def test_policy_rejection_is_sent_before_waiting_for_split_body(self):
        entered, release, finished = threading.Event(), threading.Event(), threading.Event()
        discard = Handler._discard_body
        def gated_discard(handler):
            entered.set()
            try:
                if not release.wait(2):
                    raise AssertionError('test did not release rejection drain')
                return discard(handler)
            finally:
                finished.set()
        body = json.dumps(self.request()).encode()
        headers = dict(self.headers(), **{'Content-Length': str(len(body)), 'Content-Type': 'text/plain'})
        with patch.object(Handler, '_discard_body', gated_discard):
            with socket.create_connection(('127.0.0.1', self.server.server_port), timeout=1) as conn:
                packet = 'POST /api/v1/commands HTTP/1.1\r\n' + ''.join(
                    f'{k}: {v}\r\n' for k, v in headers.items()) + '\r\n'
                conn.sendall(packet.encode())
                try:
                    self.assertTrue(entered.wait(1))
                    with http.client.HTTPResponse(conn) as response:
                        response.begin()  # Must not wait for the unsent body/drain.
                        self.assertEqual(response.status, 415)
                        self.assertEqual(json.loads(response.read())['error']['code'], 'INVALID_CONTENT_TYPE')
                    conn.sendall(body[:10])
                    time.sleep(0.02)
                    conn.sendall(body[10:])
                    conn.shutdown(socket.SHUT_WR)
                finally:
                    release.set()
                    self.assertTrue(finished.wait(1))
        self.assertEqual(self.bridge.state()['revision'], 0)

    def test_rejection_drain_has_a_byte_budget_and_absolute_deadline(self):
        # Test the bounds without depending on network timing or OS buffering.
        from unittest.mock import Mock
        handler = object.__new__(Handler)
        handler.connection = Mock()
        handler.wfile = Mock()
        handler.rfile = Mock()
        handler.rfile.read1.side_effect = lambda count: b'x' * count
        handler.headers = {'Content-Length': 'x'}
        with patch('bridge_http.time.monotonic', return_value=0):
            handler._discard_body()
        self.assertEqual(sum(c.args[0] for c in handler.rfile.read1.call_args_list), MAX_REQUEST_BYTES)
        handler.rfile.reset_mock()
        with patch('bridge_http.time.monotonic', side_effect=[0, 1]):
            handler._discard_body()
        handler.rfile.read1.assert_not_called()
        with patch('bridge_http.time.monotonic', side_effect=[0, 0.05, 0.15, 0.25]):
            handler._discard_body()
        self.assertEqual(handler.rfile.read1.call_count, 2)

    def test_repeated_complete_policy_rejections_preserve_state_and_rng(self):
        before, state, rng = self.path.read_bytes(), self.bridge.state(), random.getstate()
        body = json.dumps(self.request()).encode()
        for repeat in range(20):
            for key, value, expected in (('Content-Type', 'text/plain', 415),
                                         ('Authorization', 'Bearer wrong', 401),
                                         ('Origin', 'https://evil.example', 403)):
                with self.subTest(repeat=repeat, header=key):
                    headers = self.headers()
                    headers[key] = value
                    self.assertEqual(self.call('POST', '/api/v1/commands', body, headers)[0], expected)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.bridge.state(), state)
        self.assertEqual(random.getstate(), rng)

    def test_disconnect_during_rejection_does_not_hide_server_defects(self):
        entered, release, finished = threading.Event(), threading.Event(), threading.Event()
        errors = []
        discard = Handler._discard_body
        def observe(handler):
            entered.set()
            try:
                if not release.wait(2):
                    raise AssertionError('test did not release disconnected drain')
                return discard(handler)
            finally:
                finished.set()
        with patch.object(self.server, 'handle_error', side_effect=lambda *a: errors.append(sys.exc_info()[1])), \
                patch.object(Handler, '_discard_body', observe):
            with socket.create_connection(('127.0.0.1', self.server.server_port), timeout=1) as conn:
                # Abort rather than gracefully close: Windows uses two shorts.
                linger = struct.pack('hh' if sys.platform == 'win32' else 'ii', 1, 0)
                conn.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, linger)
                packet = (f'POST /api/v1/commands HTTP/1.1\r\nHost: {self.server.authority}\r\n'
                          'Content-Length: 1000\r\n\r\npartial').encode()
                conn.sendall(packet)
                try:
                    self.assertTrue(entered.wait(1))
                finally:
                    conn.close()
                    release.set()
            self.assertTrue(finished.wait(1))
            self.assertEqual(self.call()[0], 200)
        self.assertFalse(errors)
        self.assertEqual(self.bridge.state()['revision'], 0)

    def test_all_unsupported_methods_use_authorized_json_errors(self):
        before, rng = self.path.read_bytes(), random.getstate()
        for method in ('TRACE', 'CONNECT', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'UNKNOWN', 'HEAD'):
            with self.subTest(method=method):
                status, body, headers = self.call(method)
                self.assertEqual(status, 405)
                if method != 'HEAD':
                    self.assertEqual(body['error']['code'], 'METHOD_NOT_ALLOWED')
                    self.assertNotIn('state', body)
                else:
                    self.assertIsNone(body)
                self.assertEqual(headers['Content-Type'], 'application/json; charset=utf-8')
                self.assertEqual(headers['Cache-Control'], 'no-store')
                self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
                self.assertEqual(headers['Allow'], 'GET, POST')
                self.assertIn("frame-ancestors 'none'", headers['Content-Security-Policy'])
                self.assertNotIn('Access-Control-Allow-Origin', headers)
                unauthorized = self.headers()
                del unauthorized['Authorization']
                self.assertEqual(self.call(method, headers=unauthorized)[0], 401)
                for key, value in (('Host', 'evil.example'), ('Origin', 'https://evil.example'),
                                   ('Sec-Fetch-Site', 'cross-site')):
                    unsafe = self.headers()
                    unsafe[key] = value
                    self.assertEqual(self.call(method, headers=unsafe)[0], 403)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(random.getstate(), rng)

    def test_http_parser_errors_remain_distinct_from_api_errors(self):
        before = self.path.read_bytes()
        with socket.create_connection(('127.0.0.1', self.server.server_port), timeout=1) as conn:
            conn.sendall(b'POST /api/v1/commands EXTRA HTTP/1.1\r\n\r\n')
            conn.shutdown(socket.SHUT_WR)
            with http.client.HTTPResponse(conn) as response:
                response.begin()
                self.assertEqual(response.status, 400)
                self.assertEqual(response.getheader('Content-Type'), 'text/html;charset=utf-8')
                self.assertNotIn(b'career_id', response.read())
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
