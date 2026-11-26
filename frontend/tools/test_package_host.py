"""Packaging boundary tests plus the actual compiled local bundle integration."""
import hashlib
from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from package_host import BUNDLE_ID, HOUSING_BUNDLE_ID, REPO, package
from bridge_assets import load_bundle
from bridge_checkpoint import BridgeError


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.app = Path(self.tmp.name)
        self.dist = self.app / 'dist'
        (self.dist / 'assets').mkdir(parents=True)
        (self.dist / 'local.html').write_text('<html><script src="/assets/main.js"></script></html>')
        (self.dist / 'assets/main.js').write_text('console.info("inspection")')

    def test_deterministic_and_host_accepted(self):
        pin = package(self.dist, self.app)
        self.assertEqual(pin, package(self.dist, self.app))
        self.assertIn('/', load_bundle(self.app, BUNDLE_ID, pin).assets)

    def test_changed_candidate_cannot_replace_previous(self):
        package(self.dist, self.app)
        (self.dist / 'assets/main.js').write_text('changed')
        with self.assertRaises(ValueError): package(self.dist, self.app)

    def test_unsupported_and_nested_files_rejected(self):
        (self.dist / 'debug.map').write_text('{}')
        with self.assertRaises(ValueError): package(self.dist, self.app)

    def test_prohibited_runtime_content_rejected(self):
        (self.dist / 'assets/main.js').write_text('Court of Owls')
        with self.assertRaises(BridgeError): package(self.dist, self.app)

    def test_inline_style_rejected(self):
        (self.dist / 'local.html').write_text('<html style="color:red"></html>')
        with self.assertRaises(BridgeError): package(self.dist, self.app)

    def test_wrong_pin_rejected(self):
        package(self.dist, self.app)
        with self.assertRaises(BridgeError): load_bundle(self.app, BUNDLE_ID, '0' * 64)

    def test_actual_compiled_bundle_accepted(self):
        dist = REPO / 'frontend/dist/local'
        self.assertTrue(dist.is_dir(), 'Build local frontend before this integration suite')
        pin = package(dist, self.app)
        bundle = load_bundle(self.app, BUNDLE_ID, pin)
        self.assertIn('/', bundle.assets)
        text = '\n'.join(a.body.decode('utf-8') for a in bundle.assets.values())
        for forbidden in ('iframe:request-theme', 'host:set-theme', 'Stable life', 'Financial pressure', 'sourceMappingURL'):
            self.assertNotIn(forbidden, text)
        self.assertNotIn('<style', bundle.assets['/'].body.decode())
        self.assertEqual(pin, hashlib.sha256((self.app / 'ui_dist' / BUNDLE_ID / 'manifest.json').read_bytes()).hexdigest())


    def test_housing_candidate_is_a_separate_immutable_bundle(self):
        inspection_pin = package(self.dist, self.app)
        with self.assertRaises(ValueError):
            package(self.dist, self.app, HOUSING_BUNDLE_ID)
        housing = REPO / 'frontend/dist/housing'
        pin = package(housing, self.app, HOUSING_BUNDLE_ID)
        bundle = load_bundle(self.app, HOUSING_BUNDLE_ID, pin)
        self.assertIn(b'Gotham: The Goon - Housing', bundle.assets['/'].body)
        self.assertNotEqual(pin, inspection_pin)
        with self.assertRaises(BridgeError):
            load_bundle(self.app, BUNDLE_ID, pin)
        self.assertEqual(pin, package(housing, self.app, HOUSING_BUNDLE_ID))

    def test_invalid_candidate_never_occupies_final_release_path(self):
        (self.dist / 'local.html').write_text('<html style="color:red"></html>')
        with self.assertRaises(BridgeError): package(self.dist, self.app)
        self.assertFalse((self.app / 'ui_dist' / BUNDLE_ID).exists())


if __name__ == '__main__':
    unittest.main()
