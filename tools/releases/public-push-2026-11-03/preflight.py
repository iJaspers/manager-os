"""Bounded release checks, not a security certification or external scanner replacement.

No network, execution of scanned code, archive extraction, dependency installation,
or implicit directory traversal. A maintainer supplies explicit reviewed paths.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import io
import json
import re
import shutil
import stat
import zipfile
from release_snapshot import capture_members

MAX_FILE = 2 * 1024 * 1024
MAX_TOTAL = 16 * 1024 * 1024
MAX_MEMBERS = 300
TEXT = {'.md', '.txt', '.json', '.mjs', '.cjs', '.js', '.py', '.html', '.css', '.csv', '.yml', '.yaml', '.toml'}
RULES = {
    'PRIVATE_KEY': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'GITHUB_TOKEN': re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{30,}\b'),
    'AWS_KEY_ID': re.compile(r'\bAKIA[A-Z0-9]{16}\b'),
    'SECRET_ASSIGNMENT': re.compile(r'''(?i)["']?(?:password|api[_-]?key|access[_-]?token|client[_-]?secret)["']?\s*[:=]\s*["'][^"'\r\n]{12,}["']'''),
    'PRIVATE_RECORD_ID': re.compile(r'\blibfile_[a-f0-9]{16,}\b'),
    'PRIVATE_PATH': re.compile(r'/(?:Users|home|workspace)/[A-Za-z0-9_.-]+/'),
}
SOURCE_RISKS = re.compile(r'\b(?:eval|exec|execSync|spawnSync|subprocess\.run|fetch)\s*\(')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def safe_name(name):
    return (isinstance(name, str) and 0 < len(name) <= 240
            and not any(ord(c) < 32 or ord(c) == 127 for c in name)
            and not any(c in name for c in ('\\', ':'))
            and not name.startswith('/')
            and all(p not in ('', '.', '..') for p in name.split('/'))
            and not any(p.startswith('.') for p in name.split('/')))

class Scan:
    def __init__(self):
        self.findings = []
        self.review = []
        self.files = []
        self.total = 0
        self.members = 0

    def fail(self, path, rule, line=None):
        # Never include content, exception strings, tokens or absolute local paths.
        self.findings.append({'path': path, 'rule': rule, **({'line': line} if line else {})})

    def content(self, name, data, depth=0):
        leaf = PurePosixPath(name.rsplit('!', 1)[-1])
        self.total += len(data)
        self.members += 1
        if len(data) > MAX_FILE or self.total > MAX_TOTAL or self.members > MAX_MEMBERS:
            self.fail(name, 'SIZE_LIMIT')
            return
        self.files.append({'path': name, 'sha256': digest(data), 'bytes': len(data)})
        if leaf.suffix.lower() == '.zip':
            self.archive(name, data, depth)
            return
        if leaf.suffix.lower() not in TEXT and leaf.name not in ('LICENSE', 'NOTICE'):
            self.fail(name, 'UNREVIEWED_FILE_TYPE')
            return
        try:
            text = data.decode('utf-8', errors='strict')
        except UnicodeError:
            self.fail(name, 'NON_UTF8')
            return
        if '\x00' in text:
            self.fail(name, 'BINARY_CONTENT')
            return
        for number, line in enumerate(text.splitlines(), 1):
            for rule, pattern in RULES.items():
                matches = list(pattern.finditer(line))
                # One literal already used in WIT's negative tests, not a general
                # file/path exemption. A second assignment on the same line still fails.
                if rule == 'SECRET_ASSIGNMENT':
                    synthetic_key = "api_" + "key:'FICTIONAL-NOT-A-KEY'"
                    matches = [m for m in matches if m.group(0) != synthetic_key]
                if matches:
                    self.fail(name, rule, number)
            if leaf.suffix in {'.py', '.js', '.mjs', '.cjs'} and SOURCE_RISKS.search(line):
                self.review.append({'path': name, 'line': number, 'rule': 'SOURCE_REVIEW_REQUIRED'})
        if leaf.name == 'package.json':
            try:
                manifest = json.loads(text)
                if not isinstance(manifest, dict):
                    raise ValueError()
                if any(manifest.get(k) for k in ('dependencies', 'optionalDependencies', 'peerDependencies', 'bundledDependencies')):
                    self.fail(name, 'DEPENDENCY_REVIEW_REQUIRED')
                if manifest.get('license') != 'MIT':
                    self.fail(name, 'LICENSE_REVIEW_REQUIRED')
                scripts = manifest.get('scripts', {})
                if not isinstance(scripts, dict) or any(k in scripts for k in ('preinstall', 'install', 'postinstall', 'prepare')):
                    self.fail(name, 'INSTALL_SCRIPT_REVIEW_REQUIRED')
            except (ValueError, TypeError):
                self.fail(name, 'INVALID_MANIFEST')
        if leaf.name in ('requirements.txt', 'pyproject.toml', 'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock', 'Cargo.toml', 'Cargo.lock', 'go.mod', 'go.sum'):
            self.fail(name, 'DEPENDENCY_REVIEW_REQUIRED')

    def archive(self, name, data, depth):
        if depth >= 2:
            self.fail(name, 'ARCHIVE_DEPTH')
            return
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                seen = set()
                infos = z.infolist()
                if len(infos) > MAX_MEMBERS or z.comment:
                    self.fail(name, 'ARCHIVE_METADATA_OR_COUNT')
                    return
                members = {}
                for info in infos:
                    path = info.filename
                    # Do not reflect an unsafe member's name in logs.
                    if not safe_name(path) or path.casefold() in seen:
                        self.fail(name, 'UNSAFE_OR_DUPLICATE_MEMBER')
                        return
                    seen.add(path.casefold())
                    mode = info.external_attr >> 16
                    if (stat.S_IFMT(mode) not in (0, stat.S_IFREG) or info.flag_bits & 1
                            or info.extra or info.comment or info.is_dir()):
                        self.fail(name, 'UNSAFE_MEMBER_METADATA')
                        return
                    if (info.file_size > MAX_FILE or info.file_size + self.total > MAX_TOTAL
                            or info.file_size > max(1, info.compress_size) * 200):
                        self.fail(name, 'ARCHIVE_SIZE_LIMIT')
                        return
                    with z.open(info) as handle:
                        member = handle.read(MAX_FILE + 1)
                    members[path] = member
                    self.content(name + '!' + path, member, depth + 1)
                if 'LICENSE' not in members:
                    self.fail(name, 'MISSING_LICENSE')
                if 'SHA256SUMS.json' in members:
                    sums = json.loads(members['SHA256SUMS.json'])
                    expected = {p: digest(b) for p, b in members.items() if p != 'SHA256SUMS.json'}
                    if sums != expected:
                        self.fail(name, 'MEMBER_HASH_MISMATCH')
        except (OSError, ValueError, RuntimeError, zipfile.BadZipFile, NotImplementedError):
            self.fail(name, 'INVALID_ARCHIVE')

def scan_snapshot(root, paths, expected=None):
    scan = Scan()
    snapshot = capture_members(root, paths, scan, safe_name, MAX_FILE, expected)
    report = {'schema': 'wit.release-preflight.v1', 'passed': not scan.findings,
            'findings': scan.findings, 'source_review': scan.review, 'files': scan.files,
            'external_scanners': {n: 'AVAILABLE_NOT_RUN' if shutil.which(n) else 'NOT_INSTALLED_NOT_RUN'
                                  for n in ('gitleaks', 'osv-scanner', 'codeql')},
            'limits': 'Pattern checks and exact-file hashes only. Human privacy, licensing and source review remain required; no security certification or dependency vulnerability result.'}
    return report, snapshot

def scan_paths(root, paths, expected=None):
    return scan_snapshot(root, paths, expected)[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--manifest', type=Path, required=True, help='JSON object of reviewed relative paths to SHA-256')
    args = parser.parse_args()
    try:
        if args.manifest.stat().st_size > MAX_FILE:
            raise ValueError()
        expected = json.loads(args.manifest.read_text())
        if not isinstance(expected, dict) or not expected or len(expected) > MAX_MEMBERS or any(not isinstance(v, str) or not re.fullmatch('[a-f0-9]{64}', v) for v in expected.values()):
            raise ValueError()
        result = scan_paths(args.root, list(expected), expected)
    except (OSError, ValueError, TypeError):
        result = {'passed': False, 'findings': [{'path': '<manifest>', 'rule': 'INVALID_MANIFEST'}]}
    print(json.dumps(result, indent=2))
    return 0 if result['passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
