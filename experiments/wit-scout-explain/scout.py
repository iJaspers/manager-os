"""WIT Scout: offline, provider-neutral evidence triage. No network access."""
from dataclasses import dataclass, asdict
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from pathlib import Path
import ipaddress, json, os, re, tempfile

@dataclass(frozen=True)
class Evidence:
    title: str
    url: str
    excerpt: str
    fetched: bool = False
    official: bool = False

TRACKERS = {'utm_source','utm_medium','utm_campaign','utm_term','utm_content','fbclid','gclid'}
def canonical_url(url):
    try:
        p = urlsplit(url)
        host = (p.hostname or '').lower().rstrip('.')
        if p.scheme not in ('https','http') or not host or p.username or p.password or '\\' in url:
            return None
        if host == 'localhost' or host.endswith(('.local','.internal')):
            return None
        try:
            addr = ipaddress.ip_address(host)
            if not addr.is_global: return None
        except ValueError:
            if '.' not in host: return None
        port = p.port
        if port and not (1 <= port <= 65535): return None
        netloc = host.removeprefix('www.') + ((':'+str(port)) if port and port not in (80,443) else '')
        path = p.path.rstrip('/') or '/'
        query = urlencode(sorted((k,v) for k,v in parse_qsl(p.query, keep_blank_values=True) if k.lower() not in TRACKERS))
        return urlunsplit((p.scheme,netloc,path,query,''))
    except (ValueError, TypeError):
        return None

def normalize(items):
    seen = set(); output=[]
    for item in items:
        key = canonical_url(item.url)
        if key and key not in seen:
            seen.add(key); output.append(item)
    return output

def rank(items, goal):
    words = set(re.findall(r'[a-z0-9]{3,}',goal.lower()))
    def score(item):
        title=set(re.findall(r'[a-z0-9]{3,}',item.title.lower()))
        body=set(re.findall(r'[a-z0-9]{3,}',item.excerpt.lower()))
        return 3*len(words & title)+len(words & body)+2*item.official+item.fetched
    return sorted(normalize(items),key=score,reverse=True)

def explain(item, level='practical'):
    if level not in {'simple','practical','technical'}: raise ValueError('unknown explanation level')
    status='Full page reportedly retrieved; claims still require verification' if item.fetched else 'Search snippet only; not verified against full page'
    if level=='simple':
        return f'{item.title}\nWhat the source says: {item.excerpt}\nEvidence: {status}\nSource: {item.url}'
    if level=='practical':
        return f'Finding: {item.title}\nSource summary (not independently established): {item.excerpt}\nEvidence: {status}\nNext: inspect the original source before adoption\nSource: {item.url}'
    return f'Title: {item.title}\nURL: {item.url}\nOfficial flag (provider supplied): {item.official}\nFetched flag (provider supplied): {item.fetched}\nSource excerpt: {item.excerpt}\nVerification: {status}'

def save_checkpoint(path, items):
    """Atomic local save; caller chooses an authorized destination."""
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    payload=json.dumps({'schema':1,'items':[asdict(i) for i in normalize(items)]},ensure_ascii=False,indent=2)
    fd,tmp=tempfile.mkstemp(prefix='.scout-',dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as out:
            out.write(payload); out.flush(); os.fsync(out.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def load_checkpoint(path):
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    if data.get('schema')!=1 or not isinstance(data.get('items'),list): raise ValueError('unsupported checkpoint')
    return normalize([Evidence(**item) for item in data['items']])
