"""WIT opportunity evaluator: offline, stdlib-only, no posting or network access."""
import json, sys, hashlib
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

ALLOWED = {'reddit.com','www.reddit.com','linkedin.com','www.linkedin.com','github.com','news.ycombinator.com','stackoverflow.com'}

def canonical(url):
    p=urlsplit(url.strip())
    if p.scheme!='https' or p.hostname not in ALLOWED or p.username or p.password:
        raise ValueError('Unsupported or insecure source URL')
    path=p.path.rstrip('/') or '/'
    q=urlencode(sorted((k,v) for k,v in parse_qsl(p.query) if k in ('id',))) if p.hostname=='news.ycombinator.com' else ''
    return urlunsplit(('https',p.hostname.lower(),path,q,''))

def platform(url):
    host=urlsplit(url).hostname or ''
    return 'reddit' if 'reddit.com' in host else 'linkedin' if 'linkedin.com' in host else 'github' if host=='github.com' else 'hackernews' if host=='news.ycombinator.com' else 'stackoverflow'

def evaluate(item, seen):
    url=canonical(item['url'])
    ident=hashlib.sha256(url.encode()).hexdigest()[:16]
    reason=[]
    if ident in seen: reason.append('duplicate')
    if item.get('removed'): reason.append('removed')
    if item.get('promotional_only'): reason.append('promotion-only')
    if not item.get('verified_fit'): reason.append('no verified product fit')
    if not item.get('rules_checked'): reason.append('community rules unverified')
    if not item.get('status_checked'): reason.append('live thread status unverified')
    if not item.get('freshness_checked'): reason.append('freshness unverified')
    if not item.get('help_intent_checked'): reason.append('help intent unverified')
    if not item.get('evidence_urls'): reason.append('missing release evidence')
    score={k:max(0,min(int(item.get(k,0)),lim)) for k,lim in [('relevance',35),('help_request',25),('fit',25),('community',15)]}
    score['total']=sum(score.values())
    seen.add(ident)
    blocked=bool(reason)
    return {'schema':'wit-opportunity-v0.2','id':ident,'url':url,'platform':platform(url),'title':item.get('title',''),'score':score,'gate':'NEEDS_REVIEW' if blocked else 'PASS','gate_reasons':reason,'decision':'BLOCKED' if blocked else ('PRIORITY_REVIEW' if score['total']>=75 else 'REVIEW_LATER' if score['total']>=60 else 'ARCHIVE'),'human_approved':False,'posted_url':None,'status':'CANDIDATE','evidence_urls':item.get('evidence_urls',[])}

def run(data):
    if not isinstance(data,list): raise ValueError('Expected JSON array')
    seen=set()
    return [evaluate(x,seen) for x in data]

if __name__=='__main__':
    try: print(json.dumps(run(json.load(sys.stdin)),indent=2))
    except (ValueError,KeyError,TypeError) as exc:
        print(f'Invalid input: {exc}',file=sys.stderr);sys.exit(2)
