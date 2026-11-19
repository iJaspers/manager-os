"""Experimental, dependency-free WIT memory decision guard. No persistence or host access."""
from datetime import datetime, timezone

VALID = {"active", "superseded", "revoked"}

def select(records, key, source_commit=None):
    """Return a decision and reason; fail closed on ambiguity."""
    candidates = []
    for r in records:
        if not isinstance(r, dict) or r.get("key") != key:
            continue
        if r.get("status") not in VALID or not isinstance(r.get("id"), str):
            return {"decision": "hold", "reason": "invalid_record"}
        if r["status"] != "active":
            continue
        if r.get("sensitive") is True:
            return {"decision": "hold", "reason": "sensitive_requires_authorization"}
        if r.get("source_commit") and source_commit != r["source_commit"]:
            return {"decision": "hold", "reason": "source_revision_unverified"}
        if r.get("verified") is not True:
            return {"decision": "hold", "reason": "unverified_source"}
        candidates.append(r)
    if not candidates:
        return {"decision": "hold", "reason": "no_verified_active_record"}
    if len(candidates) != 1:
        return {"decision": "hold", "reason": "conflicting_active_records"}
    return {"decision": "use", "record_id": candidates[0]["id"]}

def once_only(checkpoint, action_id):
    """Plan only; never execute an action or claim atomic coordination."""
    if not isinstance(checkpoint, dict) or not isinstance(checkpoint.get("completed"), list):
        return {"decision": "hold", "reason": "invalid_checkpoint"}
    if action_id in checkpoint["completed"]:
        return {"decision": "skip", "reason": "already_completed"}
    return {"decision": "review", "reason": "requires_atomic_claim_and_readback"}
