"""Production scanner and builder with fictional files; no external services."""
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from preflight import scan_snapshot,scan_paths
from release_snapshot import archive_bytes

spec=importlib.util.spec_from_file_location('wit_builder',Path(__file__).with_name('build-packages.py'))
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

class SnapshotIntegration(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.versions={'fixture-one':'0.1','fixture-two':'0.1'}
        for name,version in self.versions.items():
            p=self.root/'tools'/name/version;p.mkdir(parents=True)
            (p/'LICENSE').write_text('Fictional license fixture')
            (p/'a.txt').write_text('scanned '+name)
    def build(self):
        with patch.object(builder,'ROOT',self.root),patch.object(builder,'VERSIONS',self.versions):return builder.build()
    def test_actual_builder_excludes_additions_and_modifications_after_scan(self):
        seen={}
        def mutated(root,paths):
            report,snapshot=scan_snapshot(root,paths);seen.update(snapshot)
            for name,version in self.versions.items():
                p=root/'tools'/name/version;(p/'a.txt').write_text('unscanned change');(p/'added.txt').write_text('unscanned new file')
            return report,snapshot
        with patch.object(builder,'scan_snapshot',mutated):receipts=self.build()
        for receipt in receipts:
            with zipfile.ZipFile(self.root/receipt['path']) as z:
                prefix='tools/'+receipt['id'][4:]+'/'+receipt['version']+'/'
                files={n:z.read(n) for n in z.namelist() if n!='SHA256SUMS.json'}
                self.assertEqual(files,{n[len(prefix):]:b for n,b in seen.items() if n.startswith(prefix)})
                self.assertNotIn('added.txt',files)
            self.assertTrue(scan_paths(self.root,[receipt['path']])['passed'])
    def test_failing_real_scan_writes_no_packages(self):
        p=self.root/'tools/fixture-two/0.1/a.txt';p.write_bytes(b'-----BEGIN '+b'PRIVATE KEY-----')
        with self.assertRaises(ValueError):self.build()
        self.assertFalse(list(self.root.rglob('*.zip')))
    def test_identical_rebuild_preserves_bytes(self):
        a=self.build();b=self.build();self.assertEqual(a,b)
    def test_existing_different_release_is_never_overwritten(self):
        a=self.build();path=self.root/a[0]['path'];before=path.read_bytes()
        (self.root/'tools/fixture-one/0.1/a.txt').write_text('changed source')
        with self.assertRaises(ValueError):self.build()
        self.assertEqual(path.read_bytes(),before)
    def test_symlink_output_is_not_followed(self):
        target=self.root/'untouched.txt';target.write_text('keep')
        (self.root/'tools/fixture-one/fixture-one-0.1.zip').symlink_to(target)
        with self.assertRaises(ValueError):self.build()
        self.assertEqual(target.read_text(),'keep')
    def test_member_order_does_not_change_archive(self):
        self.assertEqual(archive_bytes({'a.txt':b'a','LICENSE':b'l'}),archive_bytes({'LICENSE':b'l','a.txt':b'a'}))
    def test_generated_hashes_cover_exact_member_bytes(self):
        payload,sums,count=archive_bytes({'LICENSE':b'fictional','x.txt':b'example'})
        with zipfile.ZipFile(io.BytesIO(payload)) as z:
            self.assertEqual(z.read('SHA256SUMS.json'),sums);self.assertEqual(count,3)
            import hashlib
            self.assertEqual(json.loads(sums),{n:hashlib.sha256(z.read(n)).hexdigest() for n in ['LICENSE','x.txt']})

if __name__=='__main__':unittest.main()
