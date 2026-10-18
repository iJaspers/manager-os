import io
import json
import unittest
from unittest.mock import Mock
from gate_canary import ALLOWED_URL, RejectRedirect, decide, execute_gated_read, strict_urlopen


class Response:
    def __init__(self, data): self.data = data
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): return False
    def read(self, limit): return self.data


def good():
    return Response(json.dumps({"full_name": "iJaspers/manager-os", "private": False}).encode())


class GateTests(unittest.TestCase):
    def test_exact_gate(self):
        self.assertEqual(decide("GET_PUBLIC_REPO_METADATA", ALLOWED_URL), (True, "READ_ONLY_ADMIT"))

    def test_deny_writes_before_network(self):
        for action in ["POST", "PATCH", "PUT", "DELETE", "complete_task", "write_file", "send_email"]:
            fn = Mock(return_value=good())
            result = execute_gated_read(action, ALLOWED_URL, opener=fn)
            self.assertEqual(result["status"], "DENIED")
            fn.assert_not_called()

    def test_deny_wrong_target_before_network(self):
        for url in ["https://api.github.com/repos/other/thing", "http://api.github.com/repos/iJaspers/manager-os", ALLOWED_URL+"?x=1", "https://example.com/"]:
            fn = Mock(return_value=good())
            result = execute_gated_read("GET_PUBLIC_REPO_METADATA", url, opener=fn)
            self.assertEqual(result["status"], "DENIED")
            fn.assert_not_called()

    def test_panic(self):
        fn = Mock(return_value=good())
        result = execute_gated_read("GET_PUBLIC_REPO_METADATA", ALLOWED_URL, opener=fn, panic=True)
        self.assertEqual(result["code"], "PANIC")
        fn.assert_not_called()

    def test_good_read(self):
        fn = Mock(return_value=good())
        result = execute_gated_read("GET_PUBLIC_REPO_METADATA", ALLOWED_URL, opener=fn)
        self.assertEqual(result["status"], "VERIFIED_OBSERVATION")
        self.assertEqual(result["effect"], "NONE_READ_ONLY")
        self.assertTrue(result["evidence_sha256"])
        self.assertEqual(fn.call_count, 1)
        self.assertEqual(fn.call_args.args[0].get_method(), "GET")
        self.assertEqual(fn.call_args.args[0].full_url, ALLOWED_URL)

    def test_private_or_wrong_reply(self):
        for d in [{"full_name":"iJaspers/manager-os","private":True},{"full_name":"other/thing","private":False}, {}, [], None]:
            result = execute_gated_read("GET_PUBLIC_REPO_METADATA", ALLOWED_URL,
                                      opener=Mock(return_value=Response(json.dumps(d).encode())))
            self.assertEqual(result["status"], "UNKNOWN")

    def test_invalid_json(self):
        result = execute_gated_read("GET_PUBLIC_REPO_METADATA", ALLOWED_URL,
                opener=Mock(return_value=Response(b"NOTJSON")))
        self.assertEqual(result["code"], "BAD_JSON")

    def test_network_failure(self):
        fn=Mock(side_effect=TimeoutError("offline"))
        result=execute_gated_read("GET_PUBLIC_REPO_METADATA", ALLOWED_URL, opener=fn)
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertEqual(fn.call_count,1)

    def test_no_redirect_policy(self):
        handler = RejectRedirect()
        self.assertIsNone(handler.redirect_request(None, None, 302, "redirect", {}, "https://other.example"))
        self.assertIsNone(handler.redirect_request(None, None, 307, "redirect", {}, "https://other.example"))

    def test_real_opener_installs_reject_redirect(self):
        from unittest.mock import patch
        with patch("gate_canary.build_opener") as build:
            build.return_value.open.return_value = good()
            result = execute_gated_read("GET_PUBLIC_REPO_METADATA", ALLOWED_URL)
            self.assertEqual(result["status"], "VERIFIED_OBSERVATION")
            self.assertIsInstance(build.call_args.args[0], RejectRedirect)
            self.assertEqual(build.return_value.open.call_args.kwargs["timeout"], 8)

    def test_response_does_not_attribute_a_prior_execution(self):
        result = execute_gated_read("GET_PUBLIC_REPO_METADATA", ALLOWED_URL, opener=Mock(return_value=good()))
        self.assertEqual(result["operation_attribution"], "N/A")
        self.assertEqual(result["effect"], "NONE_READ_ONLY")

    def test_oversized_reply(self):
        fn=Mock(return_value=Response(b" "*250001))
        result=execute_gated_read("GET_PUBLIC_REPO_METADATA", ALLOWED_URL, opener=fn)
        self.assertEqual(result["code"],"UNEXPECTED_SIZE")


if __name__ == "__main__": unittest.main()
