"""Conservative semantic review gate for source-linked WIT claims.

This is NOT an LLM, an independent semantic judge or semantic entailment.
It flags simple inverted negations and prepares bounded evidence packages for
external review. It never turns a matched quote into factual approval.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from collections.abc import Mapping

from claim_review import verify_claims, _documents_index
from scout import canonical_url

_NEGATIONS = {'not', 'no', 'never', 'without'}
_STOP = {'a', 'an', 'the', 'is', 'are', 'be', 'to', 'of', 'and', 'it', 'this', 'that'}


def _tokens(text):
    normalized = re.sub(r"\b(isn|aren|doesn|don|didn|can|won|wasn|weren|hasn|haven|hadn)'t\b",
                        lambda m: m.group(1) + ' not', text.lower())
    return re.findall(r'[a-z0-9]+', normalized)


def _opposite_negation(statement, quote):
    left, right = _tokens(statement), _tokens(quote)
    # Require at least a shared three-token predicate, not an isolated word.
    # Three-token overlaps with no content words are ignored.
    for size in (5, 4, 3):
        for a in range(len(left)-size+1):
            key = left[a:a+size]
            if sum(tok not in _STOP for tok in key) < 2 or any(tok in _NEGATIONS for tok in key):
                continue
            for b in range(len(right)-size+1):
                if right[b:b+size] != key:
                    continue
                left_neg = any(t in _NEGATIONS for t in left[max(0,a-4):a])
                right_neg = any(t in _NEGATIONS for t in right[max(0,b-4):b])
                if left_neg != right_neg:
                    return True
    return False


@dataclass(frozen=True)
class InterpretationResult:
    claim_id: str
    verdict: str
    issues: tuple[str, ...]
    note: str


def review_meaning(claims, documents):
    """Second conservative gate after exact source/hash matching.

    A quote match can only yield NEEDS_SEMANTIC_REVIEW. Explicit inversion
    becomes HOLD. No automatic SUPPORTED or independent-review claim.
    """
    primary = verify_claims(claims, documents)
    index = _documents_index(documents)
    output = []
    for claim, structural in zip(claims, primary.results):
        issues = set(structural['issues'])
        if structural['verdict'] != 'HOLD':
            for entry in claim['evidence']:
                doc = index.get(canonical_url(entry['source_url']))
                if (doc and doc.sha256 == entry['sha256'] and
                    entry['quote'] in doc.text and
                    _opposite_negation(claim['statement'], entry['quote'])):
                    issues.add('POSSIBLE_NEGATION_CONFLICT')
        output.append(InterpretationResult(
            claim_id=claim['id'],
            verdict='HOLD' if issues else 'NEEDS_SEMANTIC_REVIEW',
            issues=tuple(sorted(issues)),
            note='No independent factual judgment has been performed.',
        ))
    return tuple(output)


def semantic_review_request(claims, documents):
    """Build bounded review material without copying entire source documents."""
    results = review_meaning(claims, documents)
    return {'schema': 'wit.semantic-review-request.v1',
            'classification': 'UNTRUSTED_EXTERNAL_REVIEW_INPUT',
            'requires_independent_reviewer': True,
            'questions': [
                {'claim_id': claim['id'], 'statement': claim['statement'],
                 'source_excerpts': [{'source_url': ev['source_url'], 'quote': ev['quote'],
                                      'sha256': ev['sha256']}
                                     for ev in claim['evidence']],
                 'precheck_verdict': result.verdict,
                 'precheck_issues': list(result.issues)}
                for claim, result in zip(claims, results)],
            'accepted_judgments': ['SUPPORTED', 'CONTRADICTED', 'INSUFFICIENT'],
            'independence_verified': False,
            'note': ('An external reviewer must be separately configured and its identity, '
                     'tool receipt and rationale independently validated by the host. '
                     'A requested judgment cannot authorize actions or releases.')}
