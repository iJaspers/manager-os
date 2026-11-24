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

_NEGATIONS = {'not', 'no', 'none', 'neither', 'never', 'without', 'cannot'}
_STOP = {'a', 'an', 'the', 'is', 'are', 'be', 'to', 'of', 'and', 'it', 'this', 'that'}


def _tokens(text):
    normalized = re.sub(r"\b(isn|aren|doesn|don|didn|can|won|wasn|weren|hasn|haven|hadn)'t\b",
                        lambda m: m.group(1) + ' not', text.lower())
    # Keep 'can' as a content word so 'can' versus 'cannot' aligns.
    normalized = re.sub(r'\bcannot\b', 'can not', normalized)
    return re.findall(r'[a-z0-9]+', normalized)


def _clauses(text):
    # Avoid borrowing a negation from an unrelated clause; this is only a
    # conservative precheck, not a complete grammatical parser.
    return [part for part in
            re.split(r'(?<=[.!?])\s+|[;\n]+|\b(?:but|however|yet)\b',
                     text, flags=re.IGNORECASE) if part.strip()]


def _opposite_negation(statement, quote):
    # Infix negations such as "is not" must not hide the shared predicate;
    # clause boundaries prevent unrelated "never"/"cannot" from vetoing it.
    # Still fail to NEEDS_SEMANTIC_REVIEW when meaning is too complex.
    for left_clause in _clauses(statement):
        left = _tokens(left_clause)
        left_neg = any(token in _NEGATIONS for token in left)
        left_core = [token for token in left if token not in _NEGATIONS]
        for right_clause in _clauses(quote):
            right = _tokens(right_clause)
            right_neg = any(token in _NEGATIONS for token in right)
            if left_neg == right_neg:
                continue
            right_core = [token for token in right if token not in _NEGATIONS]
            for size in (5, 4, 3):
                if len(left_core) < size or len(right_core) < size:
                    continue
                candidate_grams = {
                    tuple(left_core[i:i+size])
                    for i in range(len(left_core)-size+1)
                    if sum(token not in _STOP for token in left_core[i:i+size]) >= 2
                }
                if any(tuple(right_core[j:j+size]) in candidate_grams
                       for j in range(len(right_core)-size+1)):
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
