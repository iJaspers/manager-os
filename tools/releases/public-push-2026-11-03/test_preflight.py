"""Synthetic failure cases; no live credentials or private originals."""
import importlib.util
import io
import json
from pathlib import Path
import stat
import tempfile
import unittest
import zipfile
from preflight import scan_paths, digest, MAX_FILE

class ReleaseChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def put(self, name, data):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return name

    def scan(self, name, data):
        return scan_paths(self.root, [self.put(name, data)])

    def fails(self, report, rule):
        self.assertFalse(report['passed'])
        self.assertIn(rule, [f['rule'] for f in report['findings']])

    def archive(self, members, comment=b''):
        b = io.BytesIO()
        with zipfile.ZipFile(b, 'w') as z:
            z.comment = comment
            for name, data in members:
                z.writestr(name, data)
        return b.getvalue()

    def test_clean_source(self):
        self.assertTrue(self.scan('hello.py', b'print("synthetic")')['passed'])

    def test_private_key(self):
        self.fails(self.scan('a.txt', b'-----BEGIN ' + b'PRIVATE KEY-----'), 'PRIVATE_KEY')

    def test_token_without_reflection(self):
        token = b'gh' + b'p_' + b'x' * 36
        r = self.scan('a.txt', token)
        self.fails(r, 'GITHUB_TOKEN')
        self.assertNotIn(token.decode(), json.dumps(r))

    def test_aws_identifier(self):
        self.fails(self.scan('a.txt', b'AK' + b'IA' + b'X' * 16), 'AWS_KEY_ID')

    def test_secret_assignment(self):
        self.fails(self.scan('a.txt', b'api_' + b'key="' + b'x' * 25 + b'"'), 'SECRET_ASSIGNMENT')

    def test_private_reference(self):
        self.fails(self.scan('a.md', b'lib' + b'file_' + b'a' * 32), 'PRIVATE_RECORD_ID')

    def test_explicit_synthetic_sentinel(self):
        self.assertTrue(self.scan('a.txt', b"api_" + b"key:'FICTIONAL-NOT-A-KEY'")['passed'])

    def test_sentinel_does_not_exempt_other_assignments(self):
        self.fails(self.scan('a.txt', b"api_" + b"key:'FICTIONAL-NOT-A-KEY'; password='" + b'x' * 25 + b"'"), 'SECRET_ASSIGNMENT')

    def test_private_path(self):
        self.fails(self.scan('a.md', b'/' + b'workspace/example/private'), 'PRIVATE_PATH')

    def test_non_utf8(self):
        self.fails(self.scan('a.txt', b'\xff'), 'NON_UTF8')

    def test_binary_text(self):
        self.fails(self.scan('a.txt', b'x\x00x'), 'BINARY_CONTENT')

    def test_unknown_binary(self):
        self.fails(self.scan('a.bin', b'x'), 'UNREVIEWED_FILE_TYPE')

    def test_oversize(self):
        self.fails(self.scan('a.txt', b'x' * (MAX_FILE + 1)), 'UNSAFE_OR_MISSING_FILE')

    def test_symlink(self):
        self.put('target.txt', b'hello')
        (self.root / 'a.txt').symlink_to(self.root / 'target.txt')
        self.fails(scan_paths(self.root, ['a.txt']), 'UNSAFE_OR_MISSING_FILE')

    def test_symlink_parent(self):
        self.put('actual/a.txt', b'hello')
        (self.root / 'link').symlink_to(self.root / 'actual', target_is_directory=True)
        self.fails(scan_paths(self.root, ['link/a.txt']), 'UNSAFE_OR_MISSING_FILE')

    def test_path_traversal(self):
        self.fails(scan_paths(self.root, ['../outside.txt']), 'UNSAFE_OR_DUPLICATE_PATH')

    def test_hidden_metadata(self):
        self.fails(scan_paths(self.root, ['.git/config']), 'UNSAFE_OR_DUPLICATE_PATH')

    def test_case_collision(self):
        self.put('a.txt', b'one'); self.put('A.txt', b'two')
        self.fails(scan_paths(self.root, ['a.txt', 'A.txt']), 'UNSAFE_OR_DUPLICATE_PATH')

    def test_review_hash_change(self):
        self.put('a.txt', b'changed')
        self.fails(scan_paths(self.root, ['a.txt'], {'a.txt': digest(b'original')}), 'REVIEWED_HASH_CHANGED')

    def test_exact_review_hash(self):
        self.put('a.txt', b'original')
        self.assertTrue(scan_paths(self.root, ['a.txt'], {'a.txt': digest(b'original')})['passed'])

    def test_dependency_requires_review(self):
        self.fails(self.scan('package.json', b'{"license":"MIT","dependencies":{"unknown":"*"}}'), 'DEPENDENCY_REVIEW_REQUIRED')

    def test_license_requires_review(self):
        self.fails(self.scan('package.json', b'{"license":"UNLICENSED"}'), 'LICENSE_REVIEW_REQUIRED')

    def test_install_script_requires_review(self):
        self.fails(self.scan('package.json', b'{"license":"MIT","scripts":{"prepare":"synthetic"}}'), 'INSTALL_SCRIPT_REVIEW_REQUIRED')

    def test_python_dependencies_require_review(self):
        self.fails(self.scan('requirements.txt', b'unknown==1'), 'DEPENDENCY_REVIEW_REQUIRED')

    def test_invalid_manifest(self):
        self.fails(self.scan('package.json', b'[]'), 'INVALID_MANIFEST')

    def test_risky_source_is_review_flag_not_score(self):
        r = self.scan('a.py', b'exec("print(1)")')
        self.assertTrue(r['passed'])
        self.assertEqual(r['source_review'][0]['rule'], 'SOURCE_REVIEW_REQUIRED')

    def test_archive_hashes(self):
        members = {'LICENSE': b'MIT synthetic license fixture', 'hello.txt': b'hello'}
        sums = json.dumps({n: digest(b) for n, b in members.items()}).encode()
        r = self.scan('a.zip', self.archive([*members.items(), ('SHA256SUMS.json', sums)]))
        self.assertTrue(r['passed'], r['findings'])

    def test_archive_tamper(self):
        self.fails(self.scan('a.zip', self.archive([('LICENSE', b'MIT'), ('SHA256SUMS.json', b'{}')])), 'MEMBER_HASH_MISMATCH')

    def test_archive_missing_license(self):
        self.fails(self.scan('a.zip', self.archive([('a.txt', b'x')])), 'MISSING_LICENSE')

    def test_archive_traversal(self):
        self.fails(self.scan('a.zip', self.archive([('../secret.txt', b'x')])), 'UNSAFE_OR_DUPLICATE_MEMBER')

    def test_archive_duplicate_case(self):
        self.fails(self.scan('a.zip', self.archive([('a.txt', b'x'), ('A.txt', b'y')])), 'UNSAFE_OR_DUPLICATE_MEMBER')

    def test_archive_symlink(self):
        info = zipfile.ZipInfo('link.txt'); info.create_system = 3; info.external_attr = (stat.S_IFLNK | 0o777) << 16
        self.fails(self.scan('a.zip', self.archive([(info, b'target')])), 'UNSAFE_MEMBER_METADATA')

    def test_archive_comment(self):
        self.fails(self.scan('a.zip', self.archive([('LICENSE', b'MIT')], b'private metadata')), 'ARCHIVE_METADATA_OR_COUNT')

    def test_archive_member_extra(self):
        info = zipfile.ZipInfo('a.txt'); info.extra = b'\x01\x00\x00\x00'
        self.fails(self.scan('a.zip', self.archive([(info, b'x')])), 'UNSAFE_MEMBER_METADATA')

    def test_archive_nested_secret(self):
        self.fails(self.scan('a.zip', self.archive([('LICENSE', b'MIT'), ('a.txt', b'gh' + b'p_' + b'x'*36)])), 'GITHUB_TOKEN')

    def test_archive_depth(self):
        b = self.archive([('LICENSE', b'MIT')])
        for _ in range(2): b = self.archive([('LICENSE', b'MIT'), ('nested.zip', b)])
        self.fails(self.scan('a.zip', b), 'ARCHIVE_DEPTH')

    def test_archive_compression_bomb(self):
        b = io.BytesIO()
        with zipfile.ZipFile(b, 'w', compression=zipfile.ZIP_DEFLATED) as z: z.writestr('a.txt', b'x' * 200000)
        self.fails(self.scan('a.zip', b.getvalue()), 'ARCHIVE_SIZE_LIMIT')

    def test_external_scans_not_fabricated(self):
        r = self.scan('a.txt', b'hello')
        self.assertTrue(all(v.endswith('NOT_RUN') for v in r['external_scanners'].values()))

    def test_builder_stops_before_creating_artifacts(self):
        spec = importlib.util.spec_from_file_location('builder', Path(__file__).with_name('build-packages.py'))
        builder = importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)
        builder.ROOT = self.root; builder.VERSIONS = {'synthetic': '0.1'}
        self.put('tools/synthetic/0.1/LICENSE', b'MIT')
        self.put('tools/synthetic/0.1/bad.txt', b'gh' + b'p_' + b'x' * 36)
        with self.assertRaises(ValueError): builder.build()
        self.assertFalse(list(self.root.rglob('*.zip')))

if __name__ == '__main__':
    unittest.main()
