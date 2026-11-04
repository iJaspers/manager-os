"""Build reviewed versioned WIP ZIPs; no overwrite, network or dependency install."""
from pathlib import Path
import hashlib,json,os,stat
from preflight import scan_snapshot
from release_snapshot import archive_bytes
ROOT=Path(__file__).resolve().parents[3]
VERSIONS={'connector-doctor':'0.2.2-public-draft.1','regression-plan-forge':'0.1.1-public-draft.1','dependency-critical-path-mapper':'0.1.1-public-draft.1','source-linked-handoff-review':'0.1.0-public-draft.1'}
def save_once(path,payload):
    """Existing versioned artifacts must match exactly; never overwrite a release."""
    try:
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o644)
    except FileExistsError:
        st=path.lstat()
        if not stat.S_ISREG(st.st_mode) or st.st_nlink!=1 or path.read_bytes()!=payload:
            raise ValueError('Existing release bytes differ; select a new version')
    else:
        with os.fdopen(fd,'wb') as output:
            output.write(payload);output.flush();os.fsync(output.fileno())
    if path.is_symlink() or path.read_bytes()!=payload:raise ValueError('Release readback failed')
def build():
    # Fail before producing any package. Scans are bounded; human review remains required.
    paths=[]
    for name,version in VERSIONS.items():
        source=ROOT/'tools'/name/version
        if not (source/'LICENSE').is_file():raise ValueError('Missing scoped license')
        paths.extend(p.relative_to(ROOT).as_posix() for p in sorted(source.rglob('*')) if (p.is_file() or p.is_symlink()) and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name!='SHA256SUMS.json')
    report,snapshot=scan_snapshot(ROOT,paths)
    if not report['passed']:raise ValueError(json.dumps(report['findings']))
    receipts=[]
    for name,version in VERSIONS.items():
        source=ROOT/'tools'/name/version
        prefix=source.relative_to(ROOT).as_posix()+'/'
        files={n[len(prefix):]:data for n,data in snapshot.items() if n.startswith(prefix)}
        payload,sums,count=archive_bytes(files)
        save_once(source/'SHA256SUMS.json',sums)
        output=source.parent/(name+'-'+version+'.zip')
        save_once(output,payload)
        receipts.append({'id':'wit.'+name,'version':version,'path':output.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'size_bytes':output.stat().st_size,'members':count})
    return receipts
if __name__=='__main__':print(json.dumps(build(),indent=2))
