"""Original fictional fixtures; imports only the original repair helper."""
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from release_snapshot import capture_members, archive_bytes


class FixtureScan:
    def __init__(self, after_scan=lambda name: None):
        self.findings = []
        self.seen = {}
        self.after_scan = after_scan

    def fail(self, name, rule):
        self.findings.append((name, rule))

    def content(self, name, data):
        self.seen[name] = data
        if b'FICTIONAL-REJECT' in data:
            self.fail(name, 'FICTIONAL_RULE')
        self.after_scan(name)


def fixture_name(name):
    return isinstance(name, str) and bool(name) and not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/'))


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'LICENSE').write_bytes(b'fictional license')
        (self.root/'a.txt').write_bytes(b'clean original')

    def capture(self, scan):
        return capture_members(self.root, ['LICENSE', 'a.txt'], scan, fixture_name, 1024)

    def pack_if_passed(self, scan, snapshot):
        if scan.findings:
            raise ValueError('Fixture rejected')
        return archive_bytes(snapshot)[0]

    def members(self, payload):
        with zipfile.ZipFile(io.BytesIO(payload)) as z:
            return {n: z.read(n) for n in z.namelist()}

    def assert_binding(self, scan, payload):
        members = self.members(payload)
        sums = json.loads(members.pop('SHA256SUMS.json'))
        self.assertEqual(members, scan.seen)
        self.assertEqual(sums, {n: hashlib.sha256(b).hexdigest() for n, b in members.items()})

    def test_unchanged_positive(self):
        scan = FixtureScan(); snap = self.capture(scan)
        self.assert_binding(scan, self.pack_if_passed(scan, snap))

    def test_changed_after_scan_cannot_enter(self):
        def mutate(name):
            if name == 'a.txt': (self.root/name).write_bytes(b'FICTIONAL-REJECT')
        scan = FixtureScan(mutate); snap = self.capture(scan)
        payload = self.pack_if_passed(scan, snap)
        self.assertEqual(self.members(payload)['a.txt'], b'clean original')
        self.assert_binding(scan, payload)

    def test_added_after_scan_cannot_enter(self):
        scan = FixtureScan(lambda name: (self.root/'b.txt').write_bytes(b'FICTIONAL-REJECT'))
        snap = self.capture(scan); payload = self.pack_if_passed(scan, snap)
        self.assertNotIn('b.txt', self.members(payload)); self.assert_binding(scan, payload)

    def test_deleted_after_capture_still_uses_scanned_bytes(self):
        scan = FixtureScan(); snap = self.capture(scan)
        (self.root/'a.txt').unlink()
        self.assert_binding(scan, self.pack_if_passed(scan, snap))

    def test_snapshot_mapping_cannot_mutate(self):
        snap = self.capture(FixtureScan())
        with self.assertRaises(TypeError): snap['a.txt'] = b'changed'

    def test_preexisting_bad_bytes_rejected(self):
        (self.root/'a.txt').write_bytes(b'FICTIONAL-REJECT')
        scan = FixtureScan(); snap = self.capture(scan)
        with self.assertRaises(ValueError): self.pack_if_passed(scan, snap)

    def test_changed_before_read_is_scanned_and_rejected(self):
        def mutate(name):
            if name == 'LICENSE': (self.root/'a.txt').write_bytes(b'FICTIONAL-REJECT')
        scan = FixtureScan(mutate); snap = self.capture(scan)
        with self.assertRaises(ValueError): self.pack_if_passed(scan, snap)

    def test_duplicate_path_rejected(self):
        scan = FixtureScan()
        snap = capture_members(self.root, ['a.txt','a.txt'], scan, fixture_name, 1024)
        with self.assertRaises(ValueError): self.pack_if_passed(scan, snap)

    def test_symlink_rejected(self):
        (self.root/'link.txt').symlink_to(self.root/'a.txt')
        scan = FixtureScan()
        snap = capture_members(self.root, ['link.txt'], scan, fixture_name, 1024)
        with self.assertRaises(ValueError): self.pack_if_passed(scan, snap)

    def test_expected_hash_mismatch_rejected(self):
        scan = FixtureScan()
        snap = capture_members(self.root, ['a.txt'], scan, fixture_name, 1024, {'a.txt':'0'*64})
        with self.assertRaises(ValueError): self.pack_if_passed(scan, snap)

    def test_generated_manifest_cannot_be_input(self):
        with self.assertRaises(ValueError): archive_bytes({'SHA256SUMS.json':b'{}'})

    def test_deterministic_payload(self):
        snap = self.capture(FixtureScan())
        self.assertEqual(archive_bytes(snap), archive_bytes(snap))


if __name__ == '__main__': unittest.main(verbosity=2)
