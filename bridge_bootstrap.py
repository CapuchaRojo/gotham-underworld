"""Process-only browser pairing; never reads or mutates a career."""
from collections import deque
import hmac
import secrets
import threading
import time

from bridge_checkpoint import BridgeError

BOOTSTRAP_BYTES = 1024
CODE_SECONDS = 120
ATTEMPT_WINDOW = 60
MAX_ATTEMPTS = 10


class Bootstrap:
    def __init__(self, capability, *, clock=time.monotonic):
        self._capability = capability
        self._clock = clock
        self._lock = threading.Lock()
        self._code = None
        self._expires = 0
        self._attempts = deque()
        self._closed = False

    def issue(self):
        with self._lock:
            if self._closed:
                raise BridgeError('SESSION_CLOSED', 'Browser host is closed.', 503)
            self._code = secrets.token_urlsafe(32)
            self._expires = self._clock() + CODE_SECONDS
            return self._code

    def redeem(self, code):
        with self._lock:
            now = self._clock()
            while self._attempts and self._attempts[0] <= now - ATTEMPT_WINDOW:
                self._attempts.popleft()
            if len(self._attempts) >= MAX_ATTEMPTS:
                raise BridgeError('BOOTSTRAP_RATE_LIMIT', 'Browser authorization attempts are limited.', 429)
            self._attempts.append(now)
            matches = (isinstance(code, str) and code.isascii() and 1 <= len(code) <= 128 and
                       hmac.compare_digest(code, self._code or ''))
            if self._closed or not matches or now >= self._expires:
                raise BridgeError('BOOTSTRAP_DENIED', 'Browser authorization is unavailable.', 401)
            self._code = None  # Consume under the same lock as comparison/expiry.
            return self._capability

    def close(self):
        with self._lock:
            self._closed = True
            self._code = self._capability = None
