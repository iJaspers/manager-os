import unittest

from evidence_gate import verify_host_fetch
from research_handoff import build_handoff
from scout import Evidence


class HandoffPresentationTests(unittest.TestCase):
    def prepare(self, text, quote, *, digest=None):
        source = Evidence('Workflow reference', 'https://example.org/workflow', 'Provider marketing claim')
        doc = verify_host_fetch(source, final_url=source.url, text=text,
                                retrieval_method='trusted_search_fetch', host_verified=True)
        claim = {'id': 'limit', 'statement': quote, 'completed_action': False,
                 'evidence': [{'source_url': source.url, 'quote': quote, 'sha256': digest or doc.sha256}]}
        payload = {'results': [{'title': source.title, 'url': source.url, 'excerpt': source.excerpt}]}
        return payload, doc, claim

    def test_findings_show_relevant_evidence_below_readme_banner(self):
        quote = 'Generated outputs still require review.'
        prefix = '<!-- AUTO-GENERATED. Do not edit. -->\n<div><img src="banner.svg"></div>\n'
        payload, doc, claim = self.prepare(prefix + ('Navigation links. ' * 25) + '\n' + quote, quote)
        result = build_handoff(payload, 'review verification limits', [claim], [doc])
        self.assertIn(quote, result['findings'][0]['description'])
        self.assertNotIn('banner.svg', result['findings'][0]['description'])
        self.assertEqual(result['verdict'], 'REVIEW_REQUIRED')
        self.assertFalse(result['independent_semantic_review_completed'])

    def test_short_view_preserves_whole_quoted_negation(self):
        quote = ('The generated output in this deliberately long example, including each intermediate '
                 'result and the final narrative explanation, is never claimed as independently verified.')
        payload, doc, claim = self.prepare('# Intro\n' + quote, quote)
        result = build_handoff(payload, 'generated output', [claim], [doc], level='simple')
        self.assertIn(quote, result['findings'][0]['description'])

    def test_invalid_digest_cannot_select_a_source_passage(self):
        quote = 'A remote passage that was not validated.'
        payload, doc, claim = self.prepare('Actual introduction.\n' + ('filler ' * 100) + '\n' + quote,
                                           quote, digest='0' * 64)
        result = build_handoff(payload, 'review', [claim], [doc])
        self.assertEqual(result['verdict'], 'HOLD')
        self.assertNotIn(quote, result['findings'][0]['description'])

    def test_quote_for_another_source_cannot_describe_this_one(self):
        quote = 'Generated outputs still require review.'
        payload, doc, claim = self.prepare('Actual introduction.\n' + ('filler ' * 100) + '\n' + quote, quote)
        claim['evidence'][0]['source_url'] = 'https://other.example.org/workflow'
        result = build_handoff(payload, 'review', [claim], [doc])
        self.assertEqual(result['verdict'], 'HOLD')
        self.assertNotIn(quote, result['findings'][0]['description'])


if __name__ == '__main__':
    unittest.main()
