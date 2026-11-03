"""Rebuild only the three versioned WIP ZIPs; no network or dependency install."""
from pathlib import Path
import hashlib,json,zipfile
from preflight import scan_paths
ROOT=Path(__file__).resolve().parents[3]
VERSIONS={'connector-doctor':'0.2.1-public-draft.1','regression-plan-forge':'0.1.1-public-draft.1','dependency-critical-path-mapper':'0.1.1-public-draft.1'}
def build():
    # Fail before producing any package. Scans are bounded; human review remains required.
    paths=[]
    for name,version in VERSIONS.items():
        source=ROOT/'tools'/name/version
        if not (source/'LICENSE').is_file():raise ValueError('Missing scoped license')
        paths.extend(p.relative_to(ROOT).as_posix() for p in sorted(source.rglob('*')) if (p.is_file() or p.is_symlink()) and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name!='SHA256SUMS.json')
    report=scan_paths(ROOT,paths)
    if not report['passed']:raise ValueError(json.dumps(report['findings']))
    receipts=[]
    for name,version in VERSIONS.items():
        source=ROOT/'tools'/name/version
        files={p.relative_to(source).as_posix():p.read_bytes() for p in sorted(source.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name!='SHA256SUMS.json'}
        sums=(json.dumps({n:hashlib.sha256(b).hexdigest() for n,b in files.items()},indent=2)+'\n').encode()
        (source/'SHA256SUMS.json').write_bytes(sums);files['SHA256SUMS.json']=sums
        output=source.parent/(name+'-'+version+'.zip')
        with zipfile.ZipFile(output,'w') as z:
            for n,b in sorted(files.items()):
                info=zipfile.ZipInfo(n,(2026,11,3,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.create_system=3;info.external_attr=0o100644<<16
                z.writestr(info,b)
        receipts.append({'id':'wit.'+name,'version':version,'path':output.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'size_bytes':output.stat().st_size,'members':len(files)})
    return receipts
if __name__=='__main__':print(json.dumps(build(),indent=2))
