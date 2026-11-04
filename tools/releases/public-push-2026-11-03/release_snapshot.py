"""Capture once, scan that capture, and package only immutable captured bytes.

Original WIT repair helper. No code in input files is executed.
"""
from pathlib import Path, PurePosixPath
from types import MappingProxyType
import hashlib
import io
import json
import stat
import zipfile


def capture_members(root, paths, scan, safe_name, max_file, expected=None):
    root = Path(root).resolve()
    captured = {}
    seen = set()
    for name in tuple(paths):
        if not safe_name(name) or name.casefold() in seen:
            scan.fail('<manifest>', 'UNSAFE_OR_DUPLICATE_PATH')
            continue
        seen.add(name.casefold())
        try:
            path = root
            for part in PurePosixPath(name).parts:
                path /= part
                if path.is_symlink():
                    raise ValueError()
            st = path.stat()
            if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_size > max_file:
                raise ValueError()
            with path.open('rb') as handle:
                data = handle.read(max_file + 1)
            if expected is not None and expected.get(name) != hashlib.sha256(data).hexdigest():
                scan.fail(name, 'REVIEWED_HASH_CHANGED')
            # The exact same immutable bytes object is scanned and retained.
            scan.content(name, data)
            captured[name] = data
        except (OSError, ValueError):
            scan.fail(name, 'UNSAFE_OR_MISSING_FILE')
    return MappingProxyType(captured)


def archive_bytes(members):
    """Caller must supply only the successfully scanned snapshot subset."""
    files = dict(sorted(members.items()))
    if 'SHA256SUMS.json' in files:
        raise ValueError('Generated manifest must not be an input')
    sums = (json.dumps({n: hashlib.sha256(b).hexdigest() for n, b in files.items()}, indent=2) + '\n').encode()
    files['SHA256SUMS.json'] = sums
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 11, 3, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return out.getvalue(), sums, len(files)
