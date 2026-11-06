"""Pinned, bounded browser assets. Never serve a directory or resolve HTTP paths."""
from dataclasses import dataclass
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import re
import stat
from types import MappingProxyType

from bridge_checkpoint import BridgeError, decode_json

HOST_VERSION = 1
ENGINE_RELEASE = '1a129e83be6629b7a27c2826626856ec7fae85f7'
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_HTML_BYTES = 256 * 1024
MAX_BUNDLE_BYTES = 64 * 1024 * 1024
MAX_FILES = 256
MAX_MANIFEST_BYTES = 64 * 1024
MIME_TYPES = {
    '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8',
    '.woff2': 'font/woff2', '.png': 'image/png', '.jpg': 'image/jpeg',
    '.webp': 'image/webp', '.ico': 'image/x-icon',
}
HTML_MIME = 'text/html; charset=utf-8'
CONTENT_POLICY = ("default-src 'none'; script-src 'self'; style-src 'self'; "
                  "font-src 'self'; img-src 'self'; connect-src 'self'; "
                  "base-uri 'none'; object-src 'none'; frame-ancestors 'none'; "
                  "form-action 'none'; worker-src 'none'")
_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}')
_HASH = re.compile(r'[0-9a-f]{64}')
_FILE = re.compile(r'assets/[A-Za-z0-9][A-Za-z0-9._-]{0,127}')
_QUARANTINE = re.compile(r'court[\s_.-]*of[\s_.-]*owls|\btalons?\b', re.I)


def _require(condition):
    if not condition:
        raise BridgeError('INVALID_BUNDLE', 'Browser bundle is missing, invalid or incompatible.', 503)


def _plain(path, directory=False):
    """lstat also catches Windows junctions and other reparse points."""
    info = path.lstat()
    _require(not (getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT))
    _require(stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode))


def _bounded(path, limit):
    _plain(path)
    _require(path.stat().st_size <= limit)
    with path.open('rb') as stream:
        result = stream.read(limit + 1)
    _require(len(result) <= limit)
    return result


@dataclass(frozen=True)
class Asset:
    body: bytes
    mime: str


@dataclass(frozen=True)
class Bundle:
    bundle_id: str
    manifest_sha256: str
    assets: object  # Immutable URL -> Asset map, populated only by load_bundle.


class _IndexLinks(HTMLParser):
    def __init__(self, urls):
        super().__init__()
        self.urls = urls

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        _require(tag not in ('base', 'iframe', 'style') and 'style' not in values)
        _require(not any(name.startswith('on') for name in values))
        if tag == 'script':
            _require(bool(values.get('src')))
        for key in ('src', 'href') if tag in ('script', 'link', 'img', 'source') else ():
            if key in values:
                url = values[key]
                _require(isinstance(url, str))
                url = '/' + url if url.startswith('assets/') else url
                _require(url in self.urls)


def load_bundle(application_dir, bundle_id, manifest_sha256):
    """The hash must come from a trusted release/operator, not from the manifest."""
    try:
        _require(isinstance(bundle_id, str) and _ID.fullmatch(bundle_id) is not None)
        _require(isinstance(manifest_sha256, str) and _HASH.fullmatch(manifest_sha256) is not None)
        app = Path(application_dir).absolute()
        root = app / 'ui_dist' / bundle_id
        for directory in (app, app / 'ui_dist', root, root / 'public'):
            _plain(directory, directory=True)
        raw = _bounded(root / 'manifest.json', MAX_MANIFEST_BYTES)
        _require(hashlib.sha256(raw).hexdigest() == manifest_sha256)
        manifest = decode_json(raw.decode('utf-8'))
        _require(type(manifest) is dict and set(manifest) == {
            'asset_manifest_version', 'host_protocol_version', 'bridge_protocol_version',
            'engine_release', 'bundle_id', 'mode', 'files'})
        for key in ('asset_manifest_version', 'host_protocol_version', 'bridge_protocol_version'):
            _require(type(manifest[key]) is int and manifest[key] == 1)
        _require(manifest['engine_release'] == ENGINE_RELEASE and manifest['bundle_id'] == bundle_id)
        _require(manifest['mode'] == 'local_engine')
        files = manifest['files']
        _require(type(files) is list and 1 <= len(files) <= MAX_FILES)
        rows, total = {}, 0
        for row in files:
            _require(type(row) is dict and set(row) == {'path', 'size', 'sha256', 'mime'})
            name = row['path']
            _require(isinstance(name, str) and name not in rows)
            _require(name == 'index.html' or (_FILE.fullmatch(name) is not None and
                     Path(name).suffix in MIME_TYPES and '..' not in name))
            _require(not _QUARANTINE.search(name) and 'reference' not in name.lower())
            mime = HTML_MIME if name == 'index.html' else MIME_TYPES[Path(name).suffix]
            _require(row['mime'] == mime)
            limit = MAX_HTML_BYTES if name == 'index.html' else MAX_FILE_BYTES
            _require(type(row['size']) is int and 0 < row['size'] <= limit)
            _require(isinstance(row['sha256'], str) and _HASH.fullmatch(row['sha256']) is not None)
            total += row['size']
            _require(total <= MAX_BUNDLE_BYTES)
            rows[name] = row
        _require('index.html' in rows)
        # Only one flat assets directory is permitted; unlisted files fail startup.
        actual = set()
        for item in (root / 'public').iterdir():
            if item.name == 'assets':
                _plain(item, directory=True)
                for child in item.iterdir():
                    _plain(child)
                    actual.add('assets/' + child.name)
                    _require(len(actual) <= MAX_FILES)
            else:
                _plain(item)
                actual.add(item.name)
            _require(len(actual) <= MAX_FILES)
        _require(actual == set(rows))
        result = {}
        for name, row in rows.items():
            body = _bounded(root / 'public' / name, row['size'])
            _require(len(body) == row['size'] and hashlib.sha256(body).hexdigest() == row['sha256'])
            if name.endswith(('.html', '.js', '.css')):
                _require(not _QUARANTINE.search(body.decode('utf-8')))
            result['/' if name == 'index.html' else '/' + name] = Asset(body, row['mime'])
        _IndexLinks(set(result)).feed(result['/'].body.decode('utf-8'))
        return Bundle(bundle_id, manifest_sha256, MappingProxyType(result))
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, BridgeError) as exc:
        raise BridgeError('INVALID_BUNDLE', 'Browser bundle is missing, invalid or incompatible.', 503) from exc
