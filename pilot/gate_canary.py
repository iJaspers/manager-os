"""Private staging candidate for a PUBLIC-METADATA-ONLY GitHub Actions canary.

Independently authored, not Argus source. Only an exact allowlisted GET is possible.
Deploying this code does NOT protect other workflows, ChatGPT, Todoist, or Make.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from urllib.request import Request, HTTPRedirectHandler, build_opener

ALLOWED_URL = "https://api.github.com/repos/iJaspers/manager-os"
ALLOWED_REPO = "iJaspers/manager-os"
USER_AGENT = "MOS-Argus-ReadOnly-Canary/0"


class RejectRedirect(HTTPRedirectHandler):
    """Never follow redirects, even for apparently harmless public GETs."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def strict_urlopen(request: Request, timeout: int = 8):
    # urllib's normal opener follows 30x to a NEW URL, potentially bypassing
    # the exact target check. Explicitly forbid that automatic redirect.
    return build_opener(RejectRedirect()).open(request, timeout=timeout)


def decide(action: str, target: str, *, panic: bool = False) -> tuple[bool, str]:
    """Fail-closed, deterministic. Not a global host permission governor."""
    if panic:
        return False, "PANIC"
    if action != "GET_PUBLIC_REPO_METADATA":
        return False, "ACTION_NOT_ALLOWLISTED"
    if target != ALLOWED_URL:
        return False, "WRONG_TARGET"
    return True, "READ_ONLY_ADMIT"


def execute_gated_read(action: str, url: str, *, opener=strict_urlopen, panic=False):
    """The *only* provider access in this pilot occurs after the gate.

    No caller-supplied HTTP method or URL is accepted except exact-match constants.
    The response cannot authorize an external action.
    """
    approved, code = decide(action, url, panic=panic)
    if not approved:
        return {"status": "DENIED", "code": code, "network_called": False}
    request = Request(ALLOWED_URL, headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}, method="GET")
    try:
        with opener(request, timeout=8) as response:
            body = response.read(250001)
    except Exception:
        return {"status": "UNKNOWN", "code": "PROVIDER_READ_FAILED", "network_called": True}
    if len(body) > 250000:
        return {"status": "UNKNOWN", "code": "UNEXPECTED_SIZE", "network_called": True}
    try:
        data = json.loads(body)
    except (ValueError, UnicodeError):
        return {"status": "UNKNOWN", "code": "BAD_JSON", "network_called": True}
    if not isinstance(data, dict) or data.get("full_name") != ALLOWED_REPO or data.get("private") is not False:
        return {"status": "UNKNOWN", "code": "WRONG_OR_NONPUBLIC_REPO", "network_called": True}
    return {
        "status": "VERIFIED_OBSERVATION", "code": "READ_ONLY_REPO_MATCH", "network_called": True,
        "effect": "NONE_READ_ONLY", "operation_attribution": "N/A",
        "public_repo": ALLOWED_REPO,
        "evidence_sha256": hashlib.sha256(body).hexdigest(),
        "observed_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    result = execute_gated_read("GET_PUBLIC_REPO_METADATA", ALLOWED_URL)
    print(json.dumps(result, sort_keys=True))
    # This must fail the workflow when readback cannot be verified.
    return 0 if result["status"] == "VERIFIED_OBSERVATION" else 2


if __name__ == "__main__":
    sys.exit(main())
