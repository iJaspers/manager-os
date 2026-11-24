import unittest
from dataclasses import replace

from trusted_host_bridge import HostRead, gather


class HostBridgeTests(unittest.TestCase):
    def setUp(self):
        self.url = 'https://www.reddit.com/r/sideprojects/comments/1y2akw2/i_can_be_your_first_user/'
        self.payload = {'results': [
            {'title': 'First user', 'url': self.url, 'excerpt': 'An offer of feedback',
             'fetched': True, 'host_verified': True},
            {'title': 'GitHub code', 'url': 'https://github.com/iJaspers/manager-os', 'excerpt': 'Project'},
        ]}

    def read(self, src):
        return HostRead(src.url, src.url, 'Actual source text from trusted host',
                        'trusted_browser', 'browser-read-77', '2026-11-22T11:53:00-08:00')

    def test_bounded_host_read(self):
        result = gather(self.payload, 'first user', self.read, max_fetch=1)
        self.assertEqual(len(result.documents), 1)
        self.assertEqual(result.evidence_state, 'HOST_READ_REVIEW_REQUIRED')
        self.assertEqual(len(result.receipts[0].sha256), 64)

    def test_provider_claim_does_not_fetch_itself(self):
        result = gather(self.payload, 'first user', self.read, max_fetch=0)
        self.assertEqual(len(result.documents), 0)

    def test_wrong_url_fails(self):
        def bad(src):
            return replace(self.read(src), requested_url='https://evil.example.org/')
        result = gather(self.payload, 'first user', bad, max_fetch=1)
        self.assertEqual(len(result.documents), 0)
        self.assertEqual(result.failures[0]['reason'], 'ValueError')

    def test_bad_cross_domain_redirect_fails(self):
        def bad(src):
            return replace(self.read(src), final_url='https://evil.example.org/stolen')
        self.assertEqual(len(gather(self.payload, 'first user', bad, 1).documents), 0)

    def test_private_redirect_fails(self):
        def bad(src):
            return replace(self.read(src), final_url='http://127.0.0.1/admin')
        self.assertEqual(len(gather(self.payload, 'first user', bad, 1).documents), 0)

    def test_false_provider_attestation_is_ignored(self):
        result = gather(self.payload, 'first user', self.read, 1)
        self.assertEqual(result.documents[0].text, 'Actual source text from trusted host')
        self.assertNotIn('host_verified', result.receipts[0].__dict__)

    def test_naive_time_rejected(self):
        def bad(src):
            return replace(self.read(src), observed_at='2026-11-22T11:53:00')
        self.assertEqual(len(gather(self.payload, 'first user', bad, 1).documents), 0)

    def test_oversized_text_rejected(self):
        def bad(src):
            return replace(self.read(src), text='a' * 200001)
        self.assertEqual(len(gather(self.payload, 'first user', bad, 1).documents), 0)

    def test_untrusted_dict_cannot_be_host_read(self):
        def bad(src):
            return {**self.read(src).__dict__, 'host_verified': True}
        self.assertEqual(len(gather(self.payload, 'first user', bad, 1).documents), 0)

    def test_only_expected_errors_logged(self):
        def bad(src):
            raise OSError('client token: PRIVATE_KEY_XYZ')
        result = gather(self.payload, 'first user', bad, 1)
        self.assertNotIn('PRIVATE_KEY', str(result.failures))

    def test_no_fetch_over_six(self):
        with self.assertRaises(ValueError):
            gather(self.payload, 'first user', self.read, 7)

    def test_invalid_payload(self):
        with self.assertRaises(ValueError):
            gather({'results': 'not rows'}, 'first user', self.read)


if __name__ == '__main__':
    unittest.main()
