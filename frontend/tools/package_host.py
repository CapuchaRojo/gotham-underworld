"""Create an unapproved candidate bundle; never confer release approval."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from bridge_assets import ENGINE_RELEASE, HTML_MIME, MIME_TYPES, load_bundle

BUNDLE_ID = 'goon-c2b-inspection-v1'


def package(dist, application_dir, bundle_id=BUNDLE_ID):
    dist = Path(dist)
    if dist.is_symlink() or getattr(dist.lstat(), 'st_file_attributes', 0) & 0x400:
        raise ValueError('Reparse points are not build input')
    output = Path(application_dir) / 'ui_dist' / bundle_id
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', bundle_id):
        raise ValueError('Invalid bundle ID')
    files = {}
    for source in sorted(dist.rglob('*')):
        if source.is_symlink() or getattr(source.lstat(), 'st_file_attributes', 0) & 0x400:
            raise ValueError('Reparse points are not build input')
        if source.is_dir():
            continue
        name = source.relative_to(dist).as_posix()
        if name == 'local.html':
            name = 'index.html'
        elif not re.fullmatch(r'assets/[A-Za-z0-9][A-Za-z0-9._-]{0,127}', name):
            raise ValueError('Unexpected build output: ' + name)
        if name in files:
            raise ValueError('Duplicate build target')
        files[name] = source.read_bytes()
    rows = [dict(path=name, size=len(body), sha256=hashlib.sha256(body).hexdigest(),
                 mime=HTML_MIME if name == 'index.html' else MIME_TYPES[Path(name).suffix])
            for name, body in sorted(files.items())]
    manifest = dict(asset_manifest_version=1, host_protocol_version=1, bridge_protocol_version=1,
                    engine_release=ENGINE_RELEASE, bundle_id=bundle_id, mode='local_engine', files=rows)
    raw = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode('utf-8')
    digest = hashlib.sha256(raw).hexdigest()
    # A bundle ID is immutable once staged; changed bytes need deliberate operator removal or a new release ID.
    if output.exists():
        if (output / 'manifest.json').read_bytes() != raw:
            raise ValueError('Existing bundle differs; refusing to replace a release candidate')
    else:
        # Validate private staged bytes before publishing an immutable candidate.
        application_dir = Path(application_dir)
        application_dir.mkdir(parents=True, exist_ok=True)
        for parent in (application_dir, output.parent):
            if parent.exists() and (parent.is_symlink() or getattr(parent.lstat(), 'st_file_attributes', 0) & 0x400):
                raise ValueError('Reparse points are not publication targets')
        with tempfile.TemporaryDirectory(prefix='.c2b-stage-', dir=application_dir) as temporary:
            staged = Path(temporary) / 'ui_dist' / bundle_id
            (staged / 'public').mkdir(parents=True)
            for name, body in files.items():
                target = staged / 'public' / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(body)
            (staged / 'manifest.json').write_bytes(raw)
            load_bundle(temporary, bundle_id, digest)
            output.parent.mkdir(parents=True, exist_ok=True)
            staged.rename(output)
    load_bundle(application_dir, bundle_id, digest)
    return digest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist', type=Path, default=REPO / 'frontend/dist/local')
    parser.add_argument('--application-dir', type=Path, default=REPO)
    args = parser.parse_args()
    digest = package(args.dist, args.application_dir)
    print('UNAPPROVED candidate bundle:', BUNDLE_ID)
    print('Candidate manifest SHA-256:', digest)
    print('Validate/review source, reproducibility and content, then obtain owner approval separately.')
