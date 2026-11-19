import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from package_source import export_source, allowed

class SourceReviewTests(unittest.TestCase):
    def test_profile_saves_credentials_builds_and_archives_are_excluded(self):
        for name in ['.integration/browser/chromium-profile/Cookies','frontend/dist/local.html','ui_dist/bundle/manifest.json','.env.local','career_save.json','world_save.json','credentials.json','private.pem','data.db','old.zip','../outside.py','tests/private/career_save.json']:
            with self.subTest(name=name): self.assertFalse(allowed(name))
        for name in ['content/gotham_atlas_v1.json','career_state.py','frontend/src/App.tsx','.gitignore','frontend/tools/browser_smoke.mjs','tests/fixtures/career_m011.json','tests/institution_fixtures/.gitattributes']:
            self.assertTrue(allowed(name))
    def test_source_archive_has_verified_hashes_and_no_private_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);root=base/'source';root.mkdir();(root/'code.py').write_text('print(1)');(root/'.env').write_text('private')
            result=export_source(root,base/'review.zip',['code.py','.env'])
            self.assertEqual(result['source_files'],1)
            with zipfile.ZipFile(base/'review.zip') as archive:
                self.assertEqual(len(archive.namelist()),2)
                self.assertNotIn(b'private',b''.join(archive.read(n) for n in archive.namelist()))
    def test_hyphenated_design_words_are_not_api_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);root=base/'source';root.mkdir()
            (root/'design.md').write_text('black-mask-recruitment-authoritative-design')
            self.assertEqual(export_source(root,base/'review.zip',['design.md'])['source_files'],1)

    def test_credential_detection_never_publishes_output(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);root=base/'source';root.mkdir();(root/'bad.py').write_text('ghp_'+'x'*35)
            with self.assertRaises(ValueError):export_source(root,base/'review.zip',['bad.py'])
            self.assertFalse((base/'review.zip').exists())

if __name__=='__main__':unittest.main()
