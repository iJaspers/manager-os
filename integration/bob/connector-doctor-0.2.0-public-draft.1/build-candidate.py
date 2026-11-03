"""Build a deterministic optional WIP Bob supplement; never rewrite frozen downloads."""
from pathlib import Path
import hashlib,json,zipfile,sys
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'downloads/BOB_ON_DEMAND_2026.11.01-rc1.txt'
PIN='4fdd30e21c1251623e8bd48d2e001b3b945b533949bfc8fb8dc7ab4441280b1f'
def render():
    raw=BASE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PIN: raise ValueError('RC1 changed: stop and review base')
    body=raw.decode(); marker='\nWORKFLOW\n'
    if body.count(marker)!=1: raise ValueError('Ambiguous insertion point')
    step=Path(__file__).with_name('CONNECTOR_STEP.txt').read_text()
    return ('OPTIONAL WIP — RC1 + Connector Doctor 0.2.0-public-draft.1\nPublished WIP source; not product-accepted or automatically installed.\n\n'+body.replace(marker,'\n'+step+marker,1)).encode()
def build(destination):
    out=Path(destination);out.mkdir(parents=True,exist_ok=True)
    bob=render();name='BOB_WITH_CONNECTOR_DOCTOR_0.2.0-public-draft.1.txt';(out/name).write_bytes(bob)
    files={name:bob,'START_HERE.txt':b'Optional WIP trial: attach the Bob candidate and request one fictional task. No account or automatic installation. Existing RC1 remains unchanged. The full instructions and licence are inside the Bob text.\n'}
    archive=ROOT/'downloads/WIT_Starter_Companion_2026.11.01-rc1.zip'
    if hashlib.sha256(archive.read_bytes()).hexdigest()!='c9c977799766fc4ae5b0bf6276880795df76ae0de64c030aa8f995864d9bdf33':
        raise ValueError('RC1 archive changed: stop and review notices')
    with zipfile.ZipFile(archive) as original:
        files['NOTICE.md']=original.read('NOTICE.md')
    files['LICENSE']=Path(__file__).with_name('LICENSE').read_bytes()
    files['SHA256SUMS.json']=(json.dumps({k:hashlib.sha256(v).hexdigest() for k,v in files.items()},indent=2)+'\n').encode()
    with zipfile.ZipFile(out/'Bob_Connector_Doctor_0.2.0-public-draft.1.zip','w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(files.items()):
            i=zipfile.ZipInfo(n,(2026,11,2,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,b)
    return out
if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('Usage: python3 build-candidate.py OUTPUT_DIRECTORY')
    print(build(sys.argv[1]))
