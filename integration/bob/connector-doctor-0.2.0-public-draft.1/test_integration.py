import hashlib,importlib.util,json,tempfile,unittest,zipfile
from pathlib import Path
P=Path(__file__).parent
s=importlib.util.spec_from_file_location('builder',P/'build-candidate.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
class Integration(unittest.TestCase):
    def test_exact_base_and_additive_roundtrip(self):
        raw=b.BASE.read_bytes();candidate=b.render().decode()
        prefix='OPTIONAL WIP — RC1 + Connector Doctor 0.2.0-public-draft.1\nPublished WIP source; not product-accepted or automatically installed.\n\n'
        self.assertEqual(candidate.removeprefix(prefix).replace('\n'+(P/'CONNECTOR_STEP.txt').read_text()+'\nWORKFLOW\n','\nWORKFLOW\n',1).encode(),raw)
    def test_deterministic_fresh_install(self):
        with tempfile.TemporaryDirectory() as d:
            a=b.build(Path(d)/'a');c=b.build(Path(d)/'b')
            self.assertEqual((a/'Bob_Connector_Doctor_0.2.0-public-draft.1.zip').read_bytes(),(c/'Bob_Connector_Doctor_0.2.0-public-draft.1.zip').read_bytes())
    def test_archive_hashes_and_license(self):
        with tempfile.TemporaryDirectory() as d:
            out=b.build(d)
            with zipfile.ZipFile(out/'Bob_Connector_Doctor_0.2.0-public-draft.1.zip') as z:
                self.assertIsNone(z.testzip())
                for n,h in json.loads(z.read('SHA256SUMS.json')).items(): self.assertEqual(hashlib.sha256(z.read(n)).hexdigest(),h)
                self.assertIn(b'MIT License',z.read('BOB_WITH_CONNECTOR_DOCTOR_0.2.0-public-draft.1.txt'))
                self.assertIn(b'MIT License',z.read('LICENSE'))
                with zipfile.ZipFile(b.ROOT/'downloads/WIT_Starter_Companion_2026.11.01-rc1.zip') as original:
                    self.assertEqual(z.read('NOTICE.md'),original.read('NOTICE.md'))
    def test_wrong_base_is_refused(self):
        original=b.BASE
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'base.txt';p.write_bytes(original.read_bytes()+b'changed');b.BASE=p
            try:
                with self.assertRaises(ValueError):b.render()
            finally:b.BASE=original
    def test_frozen_rc1_zip_hashes(self):
        with zipfile.ZipFile(b.ROOT/'downloads/WIT_Starter_Companion_2026.11.01-rc1.zip') as z:
            self.assertIsNone(z.testzip())
            pins=json.loads(z.read('SHA256SUMS.json'));self.assertEqual(len(pins),5)
            for n,h in pins.items():self.assertEqual(hashlib.sha256(z.read(n)).hexdigest(),h)
    def test_private_reference_scan(self):
        import re
        self.assertIsNone(re.search(r'libfile_|@gmail|/workspace/|Bearer\s|sk-[A-Za-z0-9]{20}',b.render().decode()))
if __name__=='__main__':unittest.main()
