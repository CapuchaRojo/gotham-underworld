"""Sanitized source review exporter. No browser profiles, saves or build artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

BLOCKED = {'.git', '.integration', 'node_modules', '.venv', '.godot', '__pycache__', '.vscode', 'dist', 'ui_dist', '.vite'}
EXTENSIONS = {'.py', '.ts', '.tsx', '.md', '.json', '.css', '.html', '.yml', '.yaml', '.mjs', '.txt'}
# Versioned, synthetic migration fixtures are test source, not player progress.
TEST_FIXTURES = {'tests/fixtures/career_m011.json', 'tests/fixtures/career_m012.json',
                 'tests/fixtures/career_m013_1.json', 'tests/fixtures/m014/career.json',
                 'tests/mobility_fixtures/m015/career.json'}
SECRET = re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|(?<![A-Za-z0-9])sk-(?:proj-)?[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}')

def allowed(name):
    p = Path(name)
    if p.is_absolute() or '..' in p.parts or ':' in name or '\\' in name:
        return False
    if set(p.parts) & BLOCKED or p.name.startswith('.env'):
        return False
    if re.search(r'(?:^career.*|^world_save|credentials|cookies|login data|local state)', p.name, re.I) and p.suffix != '.py' and p.as_posix() not in TEST_FIXTURES:
        return False
    return p.name in {'.gitignore', '.gitattributes'} or p.suffix in EXTENSIONS

def export_source(root, output, names):
    root, output = Path(root).resolve(), Path(output).absolute()
    if output.is_relative_to(root):
        raise ValueError('Review archive must be outside the source tree')
    payload, excluded = {}, []
    for name in sorted(set(names)):
        if not allowed(name):
            excluded.append(name)
            continue
        path = root / name
        for item in [path, *path.parents]:
            if item == root.parent:
                break
            if item.is_symlink() or getattr(item.lstat(), 'st_file_attributes', 0) & 0x400:
                raise ValueError('Reparse source path rejected: ' + name)
        data = path.read_bytes()
        text = data.decode('utf-8')
        if SECRET.search(text):
            raise ValueError('Possible credential requires review: ' + name)
        payload[name] = data
    manifest = dict(schema=1, files={n:hashlib.sha256(b).hexdigest() for n,b in payload.items()},
                    excluded=excluded, self_excluded='SOURCE_REVIEW_MANIFEST.json')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', zipfile.ZIP_DEFLATED) as archive:
        for name, data in payload.items():
            archive.writestr('gotham-m030-c2b/' + name, data)
        archive.writestr('gotham-m030-c2b/SOURCE_REVIEW_MANIFEST.json', json.dumps(manifest, indent=2))
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError('Archive CRC verification failed')
        for name, digest in manifest['files'].items():
            assert hashlib.sha256(archive.read('gotham-m030-c2b/' + name)).hexdigest() == digest
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + '.sha256').write_text(digest + '  ' + output.name + '\n', encoding='ascii')
    return dict(zip=str(output),sha256=digest,source_files=len(payload),excluded=excluded)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(['git', '--no-optional-locks', '-C', str(root), 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], check=True, capture_output=True)
    names = [n.decode('utf-8') for n in result.stdout.split(b'\0') if n]
    print(json.dumps(export_source(root, args.output, names), indent=2))
