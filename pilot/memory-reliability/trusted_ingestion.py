"""Trust-boundary adapter for WIT memory guard. Offline and read-only.

The authority source is an explicit caller-supplied, already authenticated manifest.
This module does NOT authenticate that manifest; it rejects mixed/untrusted origins.
"""
from memory_guard import fingerprint, select

def evaluate(record, authority, *, expected_scope, current_commit):
    """Only caller-established authority may supply classifications and digests."""
    if not isinstance(authority, dict) or set(authority) != {"authenticated", "scope", "records"}:
        return {"decision":"hold","reason":"invalid_authority"}
    if authority["authenticated"] is not True:
        return {"decision":"hold","reason":"unauthenticated_authority"}
    if authority["scope"] != expected_scope or not isinstance(authority["records"],dict):
        return {"decision":"hold","reason":"authority_scope_mismatch"}
    if not isinstance(record,dict):
        return {"decision":"hold","reason":"invalid_record"}
    record_id=record.get("id")
    approved=authority["records"].get(record_id)
    if not isinstance(approved,dict) or set(approved)!={"digest","classification","source_commit"}:
        return {"decision":"hold","reason":"record_not_approved"}
    if approved["source_commit"] != current_commit:
        return {"decision":"hold","reason":"stale_authority"}
    registry={record_id:{"digest":approved["digest"],
                         "classification":approved["classification"],
                         "scope":authority["scope"]}}
    return select([record],record.get("key"),current_commit,registry,expected_scope)
