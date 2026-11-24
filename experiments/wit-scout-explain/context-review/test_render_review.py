"""Presentation boundary tests using fictional review records."""
import copy
from html.parser import HTMLParser
import unittest

from render_review import render_review


class ParsedHTML(HTMLParser):
    def __init__(self, content):
        super().__init__()
        self.tags = []
        self.attrs = []
        self.text = []
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


def example():
    url = "https://example.org/reference"
    return {
        "schema": "wit.context-memory-review.v1", "title": "A fictional research review",
        "goal": "Inspect source context and proposals", "verdict": "REVIEW_REQUIRED",
        "origin": "SYNTHETIC_DEMO", "source_details_visible": True,
        "review_binding": {"sha256": "a" * 64, "state": "NEW"},
        "context": {
            "scope": "Evidence used to construct this research report, not hidden model context.",
            "source_count": 1, "sources": [{
                "title": "Private source title", "url": url, "used_for": ["CLAIM_CHECK"],
                "reason": "Cited by the current proposal", "coverage": "COMPLETE_PINNED_FILE",
                "fetch_state": "HOST_FETCHED_TEXT", "observed_at": "2026-11-23T12:00:00Z",
                "pinned_revision": "b" * 40, "sha256": "c" * 64, "issues": [],
            }],
            "usage": {"state": "UNAVAILABLE", "input_tokens": None, "context_window": None,
                      "request_id": None, "reported_at": None, "evidence_characters": 140,
                      "evidence_tokens_estimate": 35, "estimate_scope": "SOURCE_TEXT_ONLY"},
            "limitations": ["Full sources are private unless separately cleared."],
        },
        "memory_review": {
            "owner_confirmation": "NOT_VERIFIED", "storage": "READ_ONLY_PROJECTION",
            "proposals": [{
                "id": "p1", "statement": "Keep source dates visible.", "previous_statement": None,
                "change_state": "NEW", "verdict": "REVIEW_REQUIRED",
                "issues": [], "evidence_state": "MATCHED_SOURCE_TEXT",
                "owner_confirmation": "NOT_VERIFIED", "evidence": [{
                    "source_url": url, "final_url": url, "sha256": "c" * 64,
                    "observed_sha256": "c" * 64, "quote": "A sensitive source passage.",
                    "evidence_state": "MATCHED_HOST_TEXT",
                    "navigation": {"kind": "SOURCE_PAGE_WITH_QUOTE", "url": url},
                }],
            }],
            "limitations": ["Source matching does not establish truth."],
        },
        "limitations": ["No action was performed."],
    }


class ReviewRendererTests(unittest.TestCase):
    def test_html_and_script_source_text_remain_text(self):
        data = example()
        payload = '<script>alert("owned")</script><img src=x onerror=alert(1)>'
        data["title"] = payload
        data["goal"] = payload
        data["context"]["sources"][0]["title"] = payload
        data["memory_review"]["proposals"][0]["statement"] = payload
        data["memory_review"]["proposals"][0]["previous_statement"] = payload
        data["memory_review"]["proposals"][0]["evidence"][0]["quote"] = payload
        output = render_review(data)
        parsed = ParsedHTML(output)
        self.assertNotIn("script", parsed.tags)
        self.assertNotIn("img", parsed.tags)
        self.assertNotIn("iframe", parsed.tags)
        self.assertIn(payload, "".join(parsed.text))
        self.assertFalse(any(key.startswith("on") for _, attrs in parsed.attrs for key in attrs))

    def test_attribute_quotes_cannot_create_an_event_handler(self):
        data = example()
        url = 'https://example.org/\"onmouseover=\"alert(1)'
        data["context"]["sources"][0]["url"] = url
        output = render_review(data)
        parsed = ParsedHTML(output)
        for _, attrs in parsed.attrs:
            self.assertNotIn("onmouseover", attrs)
        self.assertIn(url, [attrs.get("href") for tag, attrs in parsed.attrs if tag == "a"])

    def test_non_http_or_ambiguous_destinations_never_become_links(self):
        for url in ("javascript:alert(1)", "data:text/html,<script>x</script>", "file:///secret",
                    "//example.org/path", "https://user:password@example.org/a",
                    "https://example.org/\nnext", "https://example.org:99999/a",
                    "https:\\evil.example.org", "https://example.org/ a", "https://example.org/\x00a"):
            with self.subTest(url=url):
                data = example()
                data["context"]["sources"][0]["url"] = url
                data["memory_review"]["proposals"][0]["evidence"][0]["navigation"]["url"] = url
                parsed = ParsedHTML(render_review(data))
                external = [a["href"] for tag, a in parsed.attrs if tag == "a" and not a["href"].startswith("#")]
                self.assertEqual(external, [])

    def test_summary_ignores_accidentally_retained_source_details(self):
        data = example()
        data["source_details_visible"] = False
        output = render_review(data)
        self.assertNotIn("Private source title", output)
        self.assertNotIn("https://example.org/reference", output)
        self.assertNotIn("A sensitive source passage", output)
        self.assertIn("Keep source dates visible.", output)
        self.assertIn("Source details are hidden", output)

    def test_truthy_string_cannot_enable_source_details(self):
        data = example()
        for supplied in ("true", "false", 1, {"allowed": True}, None):
            with self.subTest(supplied=supplied):
                data["source_details_visible"] = supplied
                output = render_review(data)
                self.assertNotIn("Private source title", output)
                self.assertNotIn("A sensitive source passage", output)

    def test_source_verdict_and_owner_strings_cannot_make_approval_badges(self):
        data = example()
        data["verdict"] = "HUMAN_APPROVED"
        data["memory_review"]["owner_confirmation"] = "CONFIRMED"
        row = data["memory_review"]["proposals"][0]
        row["owner_confirmation"] = "HUMAN_APPROVED"
        row["verdict"] = "HUMAN_APPROVED"
        row["evidence_state"] = "HUMAN_APPROVED"
        output = render_review(data)
        self.assertNotIn("HUMAN_APPROVED", output)
        self.assertIn("Owner confirmation: not verified", output)
        self.assertEqual(output.count("Owner confirmation: not verified"), 1)
        self.assertIn("Review required", output)

    def test_failed_quote_check_does_not_get_verified_navigation_fallback(self):
        data = example()
        entry = data["memory_review"]["proposals"][0]["evidence"][0]
        entry["evidence_state"] = "SOURCE_HASH_MISMATCH"
        output = render_review(data)
        self.assertNotIn("Open matched source", output)
        self.assertIn("Source passage needs review", output)

    def test_unchanged_statement_does_not_hide_changed_evidence(self):
        data = example()
        data["review_binding"]["state"] = "INPUTS_CHANGED"
        data["verdict"] = "HOLD"
        data["memory_review"]["proposals"][0].update(change_state="UNCHANGED", verdict="HOLD")
        output = render_review(data)
        header = output.split("<header>", 1)[1].split("</header>", 1)[0]
        self.assertIn("Evidence changed; review again", header)
        self.assertIn("Hold for review", header)
        self.assertIn("Statement unchanged", output)
        self.assertNotIn("Evidence bundle unchanged", output)

    def test_offline_document_has_csp_and_no_active_or_remote_assets(self):
        output = render_review(example())
        parsed = ParsedHTML(output)
        for tag in ("script", "iframe", "img", "audio", "video", "object", "embed", "form", "button", "input", "link"):
            self.assertNotIn(tag, parsed.tags)
        csp = [attrs["content"] for tag, attrs in parsed.attrs if tag == "meta" and attrs.get("http-equiv") == "Content-Security-Policy"]
        self.assertEqual(len(csp), 1)
        self.assertIn("default-src 'none'", csp[0])
        self.assertIn("style-src 'unsafe-inline'", csp[0])
        self.assertIn("form-action 'none'", csp[0])
        self.assertNotIn("url(", output)
        self.assertNotIn("localStorage", output)
        self.assertNotIn("fetch(", output)

    def test_external_links_prevent_opener_and_referrer_leakage(self):
        parsed = ParsedHTML(render_review(example()))
        links = [attrs for tag, attrs in parsed.attrs if tag == "a" and attrs.get("target") == "_blank"]
        self.assertTrue(links)
        for attrs in links:
            self.assertEqual(set(attrs["rel"].split()), {"noopener", "noreferrer"})
            self.assertEqual(attrs["referrerpolicy"], "no-referrer")

    def test_usage_reports_last_request_and_keeps_evidence_estimate_separate(self):
        data = example()
        data["context"]["usage"].update(state="PROVIDER_REPORTED", input_tokens=1234,
                                           context_window=128000, request_id="synthetic-request-1",
                                           reported_at="2026-11-23T12:00:00Z")
        output = render_review(data)
        self.assertIn("1,234 input tokens", output)
        self.assertIn("Last request, as reported by the host", output)
        self.assertIn("128,000 tokens", output)
        self.assertIn("~35 tokens", output)
        self.assertIn("not the model’s prompt usage", output)
        self.assertNotIn("0.96%", output)

    def test_unknown_or_invalid_usage_never_invents_a_measurement(self):
        data = example()
        data["context"]["usage"].update(state="PROVIDER_REPORTED", context_window=None)
        for supplied in (None, True, -1, "1000"):
            with self.subTest(supplied=supplied):
                data["context"]["usage"]["input_tokens"] = supplied
                output = render_review(data)
                self.assertIn("Model usage unavailable", output)
                self.assertNotIn("Reported model window", output)

    def test_empty_records_and_missing_optional_fields_still_render(self):
        data = example()
        data["context"]["sources"] = []
        data["context"]["source_count"] = 0
        data["context"]["usage"] = {}
        data["memory_review"]["proposals"] = []
        output = render_review(data)
        self.assertIn("No sources are recorded", output)
        self.assertIn("No proposed memories are recorded", output)
        self.assertIn("Model usage unavailable", output)
        self.assertIn("<!doctype html>", render_review({}))

    def test_mobile_layout_explicitly_wraps_long_sources(self):
        output = render_review(example())
        self.assertIn('name="viewport"', output)
        self.assertIn("@media(max-width:600px)", output)
        self.assertIn("grid-template-columns:minmax(0,1fr)", output)
        self.assertIn("overflow-wrap:anywhere", output)
        self.assertIn("min-width:0", output)

    def test_render_has_no_mutation_of_the_derived_record(self):
        data = example()
        before = copy.deepcopy(data)
        first = render_review(data)
        second = render_review(data)
        self.assertEqual(data, before)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
