"""Normalize GitHub issue records for WIT. Offline; no API calls."""
from datetime import datetime, timezone
from opportunity import canonical

def adapt_issue(issue, now=None):
    if not isinstance(issue, dict):
        raise ValueError('Issue must be an object')
    url = canonical(issue['html_url'])
    if not url.startswith('https://github.com/') or '/issues/' not in url:
        raise ValueError('Not a GitHub issue URL')
    now = now or datetime.now(timezone.utc)
    created = datetime.fromisoformat(issue['created_at'].replace('Z','+00:00'))
    age_days = (now-created).total_seconds()/86400
    body = issue.get('body') or ''
    return {
        'url':url, 'title':str(issue.get('title') or '')[:500],
        'source_text':body[:4000], 'source_created_at':created.isoformat(),
        'source_author':str((issue.get('user') or {}).get('login') or ''),
        'removed':issue.get('state') != 'open' or bool(issue.get('pull_request')),
        'freshness_checked':True, 'freshness_days':round(age_days,2),
        'stale':age_days>30 or age_days<0, 'help_intent_checked':False,
        'rules_checked':False, 'status_checked':False,
        'verified_fit':False, 'evidence_urls':[],
        'relevance':0,'help_request':0,'fit':0,'community':0,
    }
