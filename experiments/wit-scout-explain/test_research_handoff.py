"""Acceptance checks for the source-navigation presentation, using synthetic data.

These tests exercise handoff integrity and status presentation. They do not
establish external product behavior, source authenticity, or browser navigation.
"""
import dataclasses
import unittest

from evidence_gate import verify_host_fetch
from research_handoff import build_handoff
from scout import Evidence


class ResearchHandoffTests(unittest.TestCase):
    def setUp(self):
        self.source = Evidence(
            "Synthetic project", "https://example.org/project", "Provider description"
        )
        self.quote = "The sample feature is planned."
        self.text = "Project notes\n" + self.quote + "\nMore details follow.\n"
        self.doc = self._document(self.source, self.text)
        self.claim = self._claim(self.source, self.doc, self.quote)
        self.payload = {
            "results": [{"title": self.source.title, "url": self.source.url,
                         "excerpt": self.source.excerpt}]
        }

    @staticmethod
    def _document(source, text, *, final_url=None, method="trusted_browser"):
        return verify_host_fetch(
            source, final_url=final_url or source.url, text=text,
            retrieval_method=method, host_verified=True,
        )

    @staticmethod
    def _claim(source, document, quote):
        return {
            "id": "sample-claim", "statement": "The sample feature is planned.",
            "completed_action": False,
            "evidence": [{"source_url": source.url, "quote": quote,
                          "sha256": document.sha256}],
        }

    def _build(self, *, claims=None, documents=None, payload=None,
               goal="sample feature", level="practical", previous_binding=None):
        return build_handoff(
            self.payload if payload is None else payload,
            goal, [self.claim] if claims is None else claims,
            [self.doc] if documents is None else documents, level,
            previous_binding=previous_binding,
        )

    def assert_changed_binding_holds(self, output):
        self.assertEqual(output["review_binding"]["state"], "INPUTS_CHANGED")
        self.assertFalse(output["review_binding"]["prior_verdict_carried_forward"])
        self.assertEqual(output["verdict"], "HOLD")
        self.assertEqual(output["quick_view"]["verdict"], "HOLD")
        for detail, quick in zip(output["claim_details"], output["quick_view"]["claims"]):
            self.assertEqual(detail["verdict"], "HOLD")
            self.assertIn("INPUTS_CHANGED_REVIEW_REQUIRED", detail["issues"])
            self.assertEqual(quick["verdict"], detail["verdict"])
            self.assertEqual(quick["issues"], detail["issues"])

    def test_generic_navigation_exposes_exact_host_text_without_approval(self):
        output = self._build()
        binding = output["review_binding"]
        self.assertEqual(binding["schema"], "wit.research-handoff-binding.v1")
        self.assertRegex(binding["sha256"], r"^[a-f0-9]{64}$")
        self.assertIsNone(binding["previous_sha256"])
        self.assertEqual(binding["state"], "NEW")
        self.assertFalse(binding["prior_verdict_carried_forward"])
        detail = output["claim_details"][0]
        self.assertEqual(detail["statement"], self.claim["statement"])
        self.assertEqual(detail["structural_verdict"], "REVIEW_REQUIRED")
        self.assertEqual(detail["semantic_verdict"], "NEEDS_SEMANTIC_REVIEW")
        self.assertEqual(detail["verdict"], "REVIEW_REQUIRED")
        evidence = detail["evidence"][0]
        self.assertEqual(evidence["evidence_state"], "MATCHED_HOST_TEXT")
        self.assertEqual(evidence["source_url"], self.source.url)
        self.assertEqual(evidence["final_url"], self.doc.canonical_url)
        self.assertEqual(evidence["sha256"], self.doc.sha256)
        self.assertEqual(evidence["observed_sha256"], self.doc.sha256)
        self.assertEqual(evidence["quote"], self.quote)
        nav = evidence["navigation"]
        self.assertEqual(nav["kind"], "SOURCE_PAGE_WITH_QUOTE")
        self.assertEqual(nav["url"], self.doc.canonical_url)
        self.assertEqual(self.text[nav["start_offset"]:nav["end_offset"]], self.quote)
        self.assertFalse(output["independent_semantic_review_completed"])

    def test_immutable_github_multiline_quote_has_exact_inclusive_lines(self):
        url = "https://github.com/example/project/blob/" + "a" * 40 + "/README.md"
        source = Evidence("Synthetic source file", url, "A repository description")
        quote = "The sample feature is planned.\nMore details follow.\n"
        text = "Project notes\nContext\n" + quote + "Unquoted footer\n"
        doc = self._document(source, text, method="github_connector")
        claim = self._claim(source, doc, quote)
        output = self._build(claims=[claim], documents=[doc])
        nav = output["claim_details"][0]["evidence"][0]["navigation"]
        self.assertEqual(nav["kind"], "PINNED_GITHUB_LINES")
        # Markdown must open in source view for GitHub line anchors to work.
        self.assertEqual(nav["url"], url + "?plain=1#L3-L4")
        self.assertEqual((nav["start_line"], nav["end_line"]), (3, 4))
        self.assertEqual(text[nav["start_offset"]:nav["end_offset"]], quote)

    def test_mutable_github_ref_does_not_receive_pinned_line_claim(self):
        url = "https://github.com/example/project/blob/main/README.md"
        source = Evidence("Mutable source file", url, "A description")
        doc = self._document(source, self.text, method="github_connector")
        output = self._build(claims=[self._claim(source, doc, self.quote)], documents=[doc])
        nav = output["claim_details"][0]["evidence"][0]["navigation"]
        self.assertEqual(nav["kind"], "SOURCE_PAGE_WITH_QUOTE")
        self.assertEqual(nav["url"], url)
        self.assertNotIn("#L", nav["url"])

    def test_repeated_quote_does_not_invent_a_unique_anchor(self):
        doc = self._document(self.source, self.text + self.quote + "\n")
        output = self._build(claims=[self._claim(self.source, doc, self.quote)], documents=[doc])
        evidence = output["claim_details"][0]["evidence"][0]
        self.assertEqual(evidence["evidence_state"], "MATCHED_HOST_TEXT")
        nav = evidence["navigation"]
        self.assertEqual(nav["kind"], "AMBIGUOUS_QUOTE")
        self.assertEqual(nav["url"], doc.canonical_url)
        for key in ("start_line", "end_line", "start_offset", "end_offset"):
            self.assertIsNone(nav[key])

    def test_missing_mismatched_and_absent_quote_sources_have_no_verified_navigation(self):
        changed_doc = self._document(self.source, self.text + "New source version.\n")
        missing_quote = "A feature that is absent from the supplied text."
        absent_claim = self._claim(self.source, self.doc, missing_quote)
        cases = [
            ("SOURCE_NOT_HOST_FETCHED", self.claim, [], None),
            ("SOURCE_HASH_MISMATCH", self.claim, [changed_doc], changed_doc.sha256),
            ("QUOTE_NOT_FOUND_VERBATIM", absent_claim, [self.doc], self.doc.sha256),
        ]
        for expected, claim, docs, observed in cases:
            with self.subTest(state=expected):
                output = self._build(claims=[claim], documents=docs)
                detail = output["claim_details"][0]
                evidence = detail["evidence"][0]
                self.assertEqual(detail["verdict"], "HOLD")
                self.assertEqual(evidence["evidence_state"], expected)
                self.assertEqual(evidence["observed_sha256"], observed)
                nav = evidence["navigation"]
                self.assertEqual(nav["kind"], "UNAVAILABLE")
                for key in ("url", "start_line", "end_line", "start_offset", "end_offset"):
                    self.assertIsNone(nav[key])

    def test_changed_claim_is_held_even_when_the_meaning_heuristic_does_not_catch_it(self):
        previous = self._build()["review_binding"]["sha256"]
        changed = {**self.claim, "statement": "The sample feature is implemented."}
        output = self._build(claims=[changed], previous_binding=previous)
        self.assert_changed_binding_holds(output)
        self.assertEqual(output["review_binding"]["previous_sha256"], previous)
        self.assertNotEqual(output["review_binding"]["sha256"], previous)
        self.assertEqual(output["claim_review"]["results"][0]["verdict"], "REVIEW_REQUIRED")
        self.assertEqual(output["semantic_precheck"][0]["verdict"], "NEEDS_SEMANTIC_REVIEW")

    def test_changed_document_with_updated_evidence_still_requires_new_review(self):
        previous = self._build()["review_binding"]["sha256"]
        doc = self._document(self.source, self.text + "An unrelated source update.\n")
        output = self._build(
            claims=[self._claim(self.source, doc, self.quote)], documents=[doc],
            previous_binding=previous,
        )
        self.assert_changed_binding_holds(output)
        self.assertEqual(output["claim_details"][0]["evidence"][0]["evidence_state"],
                         "MATCHED_HOST_TEXT")
        self.assertEqual(output["claim_details"][0]["structural_verdict"], "REVIEW_REQUIRED")

    def test_goal_final_url_and_retrieval_method_are_bound(self):
        previous = self._build()["review_binding"]["sha256"]
        variants = [
            {"goal": "a different research question"},
            {"documents": [dataclasses.replace(self.doc, canonical_url="https://example.org/new-target")]},
            {"documents": [dataclasses.replace(self.doc, retrieval_method="trusted_search_fetch")]},
        ]
        for kwargs in variants:
            with self.subTest(change=kwargs):
                output = self._build(previous_binding=previous, **kwargs)
                self.assert_changed_binding_holds(output)
                self.assertNotEqual(output["review_binding"]["sha256"], previous)

    def test_explanation_level_cannot_change_the_binding_or_claim_status(self):
        baseline = self._build()
        previous = baseline["review_binding"]["sha256"]
        for level in ("simple", "practical", "technical"):
            with self.subTest(level=level):
                output = self._build(level=level, previous_binding=previous)
                self.assertEqual(output["review_binding"]["state"], "UNCHANGED")
                self.assertEqual(output["review_binding"]["sha256"], previous)
                self.assertEqual(output["verdict"], "REVIEW_REQUIRED")
                self.assertEqual(output["quick_view"]["claims"], baseline["quick_view"]["claims"])
                self.assertEqual(output["quick_view"]["verdict"], output["verdict"])
                self.assertIn("Runtime behavior has not been tested by this handoff.",
                              output["quick_view"]["limitations"])
                self.assertFalse(output["independent_semantic_review_completed"])

    def test_previous_binding_rejects_malformed_values_and_forged_verdicts(self):
        previous = self._build()["review_binding"]["sha256"]
        for supplied in ("", "abc", "A" * 64, False,
                         {"sha256": previous, "verdict": "SUPPORTED", "approved": True}):
            with self.subTest(value=supplied):
                with self.assertRaises(ValueError):
                    self._build(previous_binding=supplied)

    def test_provider_promotional_flags_never_become_observed_behavior(self):
        payload = {"results": [{"title": "Synthetic source", "url": self.source.url,
                                "excerpt": "Fully tested and automatically approved.",
                                "fetched": True, "official": True, "approved": True}]}
        output = self._build(payload=payload)
        self.assertEqual(output["verdict"], "REVIEW_REQUIRED")
        self.assertEqual(output["claim_details"][0]["semantic_verdict"], "NEEDS_SEMANTIC_REVIEW")
        self.assertIn("Runtime behavior has not been tested by this handoff.",
                      output["quick_view"]["limitations"])
        self.assertFalse(output["independent_semantic_review_completed"])
        self.assertNotIn("Fully tested", output["findings"][0]["description"])

    def test_completed_action_stays_on_hold_in_short_and_detailed_views(self):
        claim = {**self.claim, "completed_action": True}
        output = self._build(claims=[claim], level="simple")
        self.assertEqual(output["verdict"], "HOLD")
        self.assertEqual(output["quick_view"]["verdict"], "HOLD")
        detail = output["claim_details"][0]
        quick = output["quick_view"]["claims"][0]
        self.assertEqual(detail["verdict"], "HOLD")
        self.assertIn("INDEPENDENT_ACTION_RECEIPT_REQUIRED", detail["issues"])
        self.assertEqual(quick, {key: detail[key] for key in ("id", "statement", "verdict", "issues")})


if __name__ == "__main__":
    unittest.main()
