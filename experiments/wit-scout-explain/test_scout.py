import unittest, tempfile
from pathlib import Path
from scout import Evidence,normalize,rank,explain,canonical_url,save_checkpoint,load_checkpoint
class ScoutTests(unittest.TestCase):
    def test_dedup(self):
        a=Evidence('A','https://example.com/path?utm_source=x','text')
        b=Evidence('B','https://www.example.com/path/','text')
        self.assertEqual(len(normalize([a,b])),1)
    def test_bad_urls(self):
        for url in ('file:///etc/passwd','http://127.0.0.1/x','http://localhost/x','https://user:pass@example.com','http://192.168.1.1','javascript:alert(1)'):
            self.assertIsNone(canonical_url(url),url)
    def test_ranking(self):
        a=Evidence('Other','https://a.org','none')
        b=Evidence('Memory search','https://b.org','memory search',True,True)
        self.assertEqual(rank([a,b],'memory search')[0],b)
    def test_uncertainty(self):
        x=Evidence('X','https://x.org','snippet')
        for level in ('simple','practical','technical'):
            self.assertIn('not verified',explain(x,level))
    def test_unknown_level(self):
        with self.assertRaises(ValueError): explain(Evidence('X','https://x.org','x'),'expert')
    def test_persistence_recovery(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'checkpoint.json'; items=[Evidence('A','https://example.com','text')]
            save_checkpoint(path,items); self.assertEqual(load_checkpoint(path),items)
            save_checkpoint(path,items); self.assertEqual(load_checkpoint(path),items)
    def test_invalid_checkpoint(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json';p.write_text('{"schema":2,"items":[]}')
            with self.assertRaises(ValueError): load_checkpoint(p)
    def test_no_substring_ranking(self):
        a=Evidence('memorable','https://a.org','x')
        b=Evidence('memory','https://b.org','x')
        self.assertEqual(rank([a,b],'memory')[0],b)
if __name__=='__main__':unittest.main()
