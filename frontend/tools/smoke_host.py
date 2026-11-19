"""Explicit test-fixture preparation, then read-only browser-host execution."""
import argparse
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from bridge_assets import load_bundle
from browser_host import BrowserHost
from engine_bridge import Bridge
from package_host import BUNDLE_ID

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('mode', choices=('prepare', 'serve'))
parser.add_argument('--directory', type=Path, required=True)
parser.add_argument('--test-pin')
args = parser.parse_args()
checkpoint = args.directory / 'inspection.bridge.json'
if args.mode == 'prepare':
    args.directory.mkdir(parents=True, exist_ok=True)
    with Bridge.create(checkpoint, 42) as bridge:
        for i, command in enumerate(('settle_in', 'wait')):
            state = bridge.state()
            bridge.execute(dict(protocol_version=1, career_id=state['career_id'], lineage_id=state['lineage_id'],
                request_id=f'operator-fixture-{i}', expected_revision=state['revision'], command=command, arguments={}))
else:
    # The harness supplies a reviewed test-candidate pin, never a production approval.
    bundle = load_bundle(REPO, BUNDLE_ID, args.test_pin)
    with BrowserHost.open(checkpoint, args.directory / 'host.json', bundle) as host:
        host.start()
        print(json.dumps(dict(origin=host.server.origin, code=host.server.bootstrap.issue())), flush=True)
        input()  # Parent terminates this explicit test host by closing its input.
