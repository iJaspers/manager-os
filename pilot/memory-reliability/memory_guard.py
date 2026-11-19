"""Experimental WIT memory eligibility guard. No I/O, storage, or execution.
Trusted registry MUST come independently from an authenticated source.
"""
import hashlib
import json

FIELDS = frozenset(("id", "key", "status", "source_commit"))
TRUST_FIELDS = frozenset(("digest", "classification", "scope"))
STATUSES = frozenset(("active", "superseded", "revoked"))

def fingerprint(record):
    if not isinstance(record, dict) or set(record) != FIELDS:
        raise ValueError("invalid_record_schema")
    if any(not isinstance(record[k], str) or not record[k] for k in FIELDS):
        raise ValueError("invalid_record_values")
    if record["status"] not in STATUSES:
        raise ValueError("invalid_status")
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode()).hexdigest()

def select(records, key, source_commit=None, trusted_sources=None, scope=None):
    if not isinstance(records, list) or not isinstance(key, str) or not key:
        return {"decision": "hold", "reason": "invalid_input"}
    if not isinstance(trusted_sources, dict) or not isinstance(scope, str) or not scope:
        return {"decision": "hold", "reason": "missing_trust_context"}
    candidates, seen = [], set()
    for record in records:
        try:
            digest = fingerprint(record)
        except (ValueError, TypeError):
            return {"decision": "hold", "reason": "invalid_record"}
        if record["id"] in seen:
            return {"decision": "hold", "reason": "duplicate_record_id"}
        seen.add(record["id"])
        if record["key"] != key or record["status"] != "active":
            continue
        trust = trusted_sources.get(record["id"])
        if not isinstance(trust, dict) or set(trust) != TRUST_FIELDS:
            return {"decision": "hold", "reason": "untrusted_record"}
        if trust["digest"] != digest:
            return {"decision": "hold", "reason": "provenance_mismatch"}
        if trust["classification"] != "non_sensitive":
            return {"decision": "hold", "reason": "privacy_review_required"}
        if trust["scope"] != scope:
            return {"decision": "hold", "reason": "scope_mismatch"}
        if record["source_commit"] != source_commit:
            return {"decision": "hold", "reason": "source_revision_unverified"}
        candidates.append(record)
    if not candidates:
        return {"decision": "hold", "reason": "no_eligible_record"}
    if len(candidates) != 1:
        return {"decision": "hold", "reason": "conflicting_active_records"}
    return {"decision": "use", "record_id": candidates[0]["id"]}

def once_only(checkpoint, action_id):
    """Planning hint only: NOT an atomic lock or execution authorization."""
    if not isinstance(action_id, str) or not action_id:
        return {"decision": "hold", "reason": "invalid_action_id"}
    if (not isinstance(checkpoint, dict) or set(checkpoint) != {"completed"}
            or not isinstance(checkpoint["completed"], list)
            or any(not isinstance(x, str) for x in checkpoint["completed"])):
        return {"decision": "hold", "reason": "invalid_checkpoint"}
    if action_id in checkpoint["completed"]:
        return {"decision": "skip", "reason": "already_completed"}
    return {"decision": "review", "reason": "requires_atomic_claim_and_readback"}
