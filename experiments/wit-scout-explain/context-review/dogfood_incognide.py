"""Replay five actual, host-captured public GitHub reads through existing Scout.

The transfer and its digest must come from the trusted host, not from a source
or a model's assertion. This finite acceptance exercise performs no network
access. It writes a new output directory and uses the existing checkpoint API.
Full source checkpoints/connector transfers are working evidence: do not commit
them. Only the bounded derived report and metadata receipt are public candidates.
"""
from __future__ import annotations

import argparse
import copy
from dataclasses import replace
from datetime import datetime
import hashlib
import hmac
import json
from pathlib import Path
import subprocess
import sys

from _base import BASE_COMMIT, ResearchSession, _decode, gather, save_research_checkpoint
from github_connector_adapter import GitHubConnectorAdapter, GitHubTarget
from render_review import render_review
from review import write_new
from review_view import build_review_view

INCOGNIDE_COMMIT = "5f302fd4a8bbd2beffb6301608bed7acde0e619d"
SOURCES = (
    ("NPC-Worldwide/incognide", "src/renderer/components/ContextFilesPanel.tsx", INCOGNIDE_COMMIT,
     "Context controls", "The context panel includes a Clear all control.", 'title="Clear all"'),
    ("NPC-Worldwide/incognide", "src/renderer/components/MemoryManagement.tsx", INCOGNIDE_COMMIT,
     "Memory review", "The memory view can display the original proposed memory.",
     "Original: {memory.initial_memory}"),
    ("NPC-Worldwide/incognide", "src/renderer/utils/contextUsage.ts", INCOGNIDE_COMMIT,
     "Usage reporting", "The usage helper prefers the reported token count when available.",
     "if (reported !== null) return { used: reported, source: 'reported' };"),
    ("NPC-Worldwide/incognide", "src/npc_team/jinxes/kg/knowledge_approve.jinx", INCOGNIDE_COMMIT,
     "Approval labels", "An approval workflow input defaults to human-approved.",
     '{ status: "human-approved" }'),
    ("iJaspers/manager-os", "tools/scout-explain/0.1.0-public-draft.1/research_checkpoint.py", BASE_COMMIT,
     "Existing recovery", "The recovery contract says not to take expected anchors from the checkpoint itself.",
     "Never take expected_sha256 or approved_urls from the checkpoint itself."),
)


def run(transfer_path, expected_digest, output_directory):
    if not isinstance(expected_digest, str) or len(expected_digest) != 64:
        raise ValueError("Externally retained transfer digest required")
    with Path(transfer_path).open("rb") as stream:
        raw = stream.read(500_001)
    if len(raw) > 500_000 or not hmac.compare_digest(hashlib.sha256(raw).hexdigest(), expected_digest):
        raise ValueError("Host transfer bytes changed or exceed the bound")
    transfer = _decode(raw)
    if type(transfer) is not dict or set(transfer) != {"observed_at", "entries"}:
        raise ValueError("Unexpected host transfer schema")
    entries = transfer["entries"]
    if type(entries) is not list or len(entries) != len(SOURCES):
        raise ValueError("Expected exactly five reviewed public source responses")
    received = {}
    for entry in entries:
        if type(entry) is not dict or set(entry) != {"repository", "path", "ref", "response"}:
            raise ValueError("Invalid transfer entry")
        key = (entry["repository"], entry["path"], entry["ref"])
        if key in received:
            raise ValueError("Duplicate source response")
        received[key] = entry["response"]
    if set(received) != {source[:3] for source in SOURCES}:
        raise ValueError("Host transfer targets differ from the pinned source plan")
    observed = datetime.fromisoformat(transfer["observed_at"].replace("Z", "+00:00"))
    targets = tuple(GitHubTarget(*source[:3]) for source in SOURCES)

    def captured_fetch(*, repository_full_name, path, ref):
        return received[(repository_full_name, path, ref)]

    adapter = GitHubConnectorAdapter(captured_fetch, targets, clock=lambda: observed)
    goal = "Review Incognide context and memory patterns alongside WIT research recovery"
    payload = {"results": [
        {"title": source[3], "url": target.url,
         "excerpt": "Host-selected pinned source for a bounded context and memory review."}
        for source, target in zip(SOURCES, targets)]}
    gathered = gather(payload, goal, adapter, max_fetch=len(targets))
    if len(gathered.documents) != len(targets) or gathered.failures:
        raise ValueError("The actual source replay did not validate every pinned file")
    docs = {doc.source.url: doc for doc in gathered.documents}
    claims = tuple({
        "id": f"pattern-{index + 1}", "statement": source[4], "completed_action": False,
        "evidence": [{"source_url": target.url, "quote": source[5],
                      "sha256": docs[target.url].sha256}],
    } for index, (source, target) in enumerate(zip(SOURCES, targets)))
    allowed = tuple(target.url for target in targets)
    session = ResearchSession(payload, goal, claims, gathered, BASE_COMMIT, allowed)
    report = build_review_view(session, include_source_details=True, origin="HOST_SOURCE_REPLAY")
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=False)
    checkpoint = output / "source_checkpoint_PRIVATE_WORKING.json"
    digest = save_research_checkpoint(checkpoint, payload=payload, goal=goal, claims=claims,
        gathered=gathered, code_revision=BASE_COMMIT, approved_urls=allowed)
    script = (
        "import json,sys;sys.path.insert(0,sys.argv[1]);"
        "from _base import load_research_checkpoint;from review_view import build_review_view;"
        "s=load_research_checkpoint(sys.argv[2],expected_sha256=sys.argv[3],"
        "expected_code_revision=sys.argv[4],approved_urls=tuple(json.loads(sys.argv[5])));"
        "print(json.dumps(build_review_view(s,include_source_details=True,origin='HOST_SOURCE_REPLAY')))"
    )
    restored = subprocess.run([sys.executable, "-I", "-c", script,
        str(Path(__file__).resolve().parent), str(checkpoint), digest, BASE_COMMIT,
        json.dumps(allowed)], capture_output=True, text=True, timeout=20, check=True)
    if json.loads(restored.stdout) != report:
        raise AssertionError("Fresh-process recovery changed the review view")
    forged = copy.deepcopy(claims[0])
    forged["owner_confirmed"] = True
    try:
        build_review_view(replace(session, claims=(forged,) + claims[1:]))
    except ValueError:
        forged_rejected = True
    else:
        raise AssertionError("A forged approval field was admitted")
    changed = copy.deepcopy(claims[0])
    changed["statement"] += " Installation is complete."
    changed["completed_action"] = True
    changed_view = build_review_view(replace(session, claims=(changed,) + claims[1:]),
                                     previous_session=session)
    if (changed_view["verdict"] != "HOLD" or
            changed_view["review_binding"]["state"] != "INPUTS_CHANGED"):
        raise AssertionError("Changed completion claim was not held")
    html = render_review(report)
    write_new(output / "incognide_review.html", html)
    write_new(output / "incognide_review.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    receipt = {
        "schema": "wit.context-review-dogfood-receipt.v1",
        "observed_at": transfer["observed_at"], "base_commit": BASE_COMMIT,
        "incognide_commit": INCOGNIDE_COMMIT,
        "mode": "Actual host connector reads replayed offline; no model inference or live deployed host",
        "host_transfer_sha256": expected_digest,
        "source_count": len(docs), "proposal_count": len(claims),
        "verdict": report["verdict"],
        "proposal_verdicts": {item["id"]: item["verdict"] for item in report["memory_review"]["proposals"]},
        "owner_confirmation": report["memory_review"]["owner_confirmation"],
        "fresh_process_restore_identical": True,
        "checkpoint_sha256": digest, "forged_approval_rejected": forged_rejected,
        "changed_completion_claim": "HOLD / INPUTS_CHANGED",
        "html_sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
        "sources": [{"url": doc.source.url, "sha256": doc.sha256,
                     "retained_utf8_bytes": len(doc.text.encode("utf-8"))}
                    for doc in gathered.documents],
        "limits": ["No independent factual or semantic acceptance",
                   "No Incognide installation or runtime testing",
                   "No memory write, approval mutation or action dispatch",
                   "Rendered-browser and physical-device acceptance separate"],
    }
    write_new(output / "DOGFOOD_RECEIPT.json", json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host-transfer", required=True, type=Path)
    parser.add_argument("--transfer-sha256", required=True)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.host_transfer, args.transfer_sha256, args.output_directory), indent=2))
