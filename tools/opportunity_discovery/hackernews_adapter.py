"""Normalize official Hacker News item records, without making network calls."""
from datetime import datetime, timezone
from opportunity import canonical

def adapt_item(item, now=None):
    if not isinstance(item,dict) or not isinstance(item.get('id'),int) or isinstance(item.get('id'),bool) or item['id']<=0:
        raise ValueError('Invalid Hacker News item')
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None: raise ValueError('Timezone-aware clock required')
    when=datetime.fromtimestamp(item['time'],timezone.utc)
    age=(now-when).total_seconds()/86400
    return {
        'url':canonical(f"https://news.ycombinator.com/item?id={item['id']}"),
        'title':str(item.get('title') or '')[:500],
        'source_text':str(item.get('text') or '')[:4000],
        'source_created_at':when.isoformat(),
        'source_author':str(item.get('by') or ''),
        'removed':bool(item.get('deleted') or item.get('dead')),
        'stale':age<0 or age>30,
        'freshness_checked':True,
        'help_intent_checked':False,
        'rules_checked':False,
        'status_checked':False,
        'verified_fit':False,
        'evidence_urls':[],
        'relevance':0,'help_request':0,'fit':0,'community':0,
    }
