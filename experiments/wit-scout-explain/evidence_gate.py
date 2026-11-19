"""Evidence gate for host-fetched content. Host, not Scout, owns network access.

Do not call untrusted URLs directly. The host must enforce public-IP DNS resolution,
redirect revalidation, timeouts, content limits and explicit tool permissions.
"""
from dataclasses import dataclass
from scout import Evidence, canonical_url
import hashlib

MAX_TEXT=200_000

@dataclass(frozen=True)
class VerifiedDocument:
    source: Evidence
    canonical_url: str
    sha256: str
    text: str
    retrieval_method: str

def verify_host_fetch(source, *, final_url, text, retrieval_method, host_verified=False):
    """Promote a host fetch only after explicit trusted host attestation.

    host_verified MUST be set by the trusted caller, never copied from search results.
    This verifies handoff integrity, not the truth of claims in the page.
    """
    if not isinstance(source,Evidence): raise TypeError('source must be Evidence')
    original=canonical_url(source.url)
    final=canonical_url(final_url)
    if not original or not final: raise ValueError('invalid source URL')
    if not host_verified: raise PermissionError('trusted host verification required')
    if not isinstance(text,str) or not text.strip() or len(text)>MAX_TEXT: raise ValueError('invalid page content')
    if retrieval_method not in ('github_connector','trusted_browser','trusted_search_fetch'):
        raise ValueError('unknown trusted retrieval method')
    return VerifiedDocument(source,final,hashlib.sha256(text.encode('utf-8')).hexdigest(),text,retrieval_method)

def source_excerpt(doc, phrase, context=140):
    """Exact textual match; absence is reported, never invented."""
    if not isinstance(doc,VerifiedDocument): raise TypeError('verified document required')
    if not isinstance(phrase,str) or not phrase or len(phrase)>200: raise ValueError('invalid phrase')
    at=doc.text.casefold().find(phrase.casefold())
    if at<0: return None
    return doc.text[max(0,at-context):min(len(doc.text),at+len(phrase)+context)]
