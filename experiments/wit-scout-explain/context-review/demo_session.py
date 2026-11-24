"""Fictional offline inputs; these are not live source or human-review receipts."""
from _base import Gathered, HostRead, ResearchSession, gather


def make_demo_session():
    payload = {"results": [
        {"title": "Workshop workflow review guide", "url": "https://example.org/guide",
         "excerpt": "A workflow guide with a review step."},
        {"title": "Workshop workflow review archive", "url": "https://example.org/archive",
         "excerpt": "An older lead whose original could not be retrieved."},
        {"title": "Related workshop", "url": "https://example.org/related",
         "excerpt": "A supplied snippet awaiting retrieval."},
    ]}
    text = "# Fictional guide\nThe workshop workflow requires review before adoption.\n"

    def fictional_fetch(source):
        if source.url.endswith("/archive"):
            raise TimeoutError("Synthetic failure")
        return HostRead(source.url, source.url, text, "trusted_search_fetch",
                        "synthetic-example-only", "2026-11-23T20:00:00-07:00")

    goal = "Review the workshop workflow"
    gathered = gather(payload, goal, fictional_fetch, max_fetch=2)
    claims = (
        {"id": "review-step", "statement": "The workflow requires review before adoption.",
         "completed_action": False, "evidence": [
             {"source_url": "https://example.org/guide",
              "quote": "The workshop workflow requires review before adoption.",
              "sha256": gathered.documents[0].sha256}]},
        {"id": "archive-note", "statement": "The archive contains the same review step.",
         "completed_action": False, "evidence": [
             {"source_url": "https://example.org/archive", "quote": "Review before adoption.",
              "sha256": "0" * 64}]},
    )
    return ResearchSession(payload, goal, claims, gathered, "fictional-context-demo-v1",
                           ("https://example.org/guide", "https://example.org/archive"))
