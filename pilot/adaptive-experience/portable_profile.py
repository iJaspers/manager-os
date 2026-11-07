#!/usr/bin/env python3
"""Validate a WIT portable style profile as untrusted data, with no writes or host actions.

This is a local, deterministic guard for the optional WIT adaptive-experience pilot.
It does not establish user consent, authenticate identity, read host memory, or import
preferences into an AI host. Imported cards require the user's confirmation.
"""

import argparse
import json
import re
from pathlib import Path

FORMAT = "wit.portable.preferences.v1"
MAX_BYTES = 4096
MAX_STYLES = 8
LEVELS = ("Everyday", "Power", "Super")
SAFE_STYLES = {
    "concise_answers": "Keep answers concise",
    "one_next_action": "Give one clear next action",
    "step_by_step": "Explain tasks step by step",
    "technical_depth": "Include technical depth when relevant",
    "plain_language": "Prefer plain language",
    "useful_examples": "Include useful concrete examples",
    "compare_options": "Compare options and tradeoffs",
    "tables_when_useful": "Use tables when they improve clarity",
    "ask_fewer_questions": "Ask fewer optional questions",
    "evidence_first": "Distinguish verified evidence from assumptions",
    "short_recaps": "Use short progress recaps",
}
EXPECTED_KEYS = {"format", "level", "scope", "styles"}
SCOPE_KEYS = {"kind", "project_name"}
PROJECT_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _.-]{0,63}$")


class InvalidProfile(ValueError):
    pass


def _reject_duplicates(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise InvalidProfile(f"Duplicate key: {key}")
        obj[key] = value
    return obj


def validate_profile(raw):
    """Return a sanitized, fixed-vocabulary profile or raise InvalidProfile.

    Approval cannot be established by the card itself. This function never
    executes any instruction appearing in input and never saves anything.
    """
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    if not isinstance(raw, bytes):
        raise InvalidProfile("Input must be UTF-8 bytes or text")
    if len(raw) > MAX_BYTES:
        raise InvalidProfile("Profile exceeds 4096-byte limit")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise InvalidProfile("Invalid UTF-8") from exc
    try:
        profile = json.loads(text, object_pairs_hook=_reject_duplicates)
    except (json.JSONDecodeError, UnicodeDecodeError, RecursionError) as exc:
        raise InvalidProfile("Malformed JSON") from exc
    if not isinstance(profile, dict) or set(profile) != EXPECTED_KEYS:
        raise InvalidProfile("Unexpected or missing top-level keys")
    if profile["format"] != FORMAT:
        raise InvalidProfile("Unsupported profile format")
    if type(profile["level"]) is not str or profile["level"] not in LEVELS:
        raise InvalidProfile("Invalid experience level")
    scope = profile["scope"]
    if not isinstance(scope, dict):
        raise InvalidProfile("Invalid scope")
    if scope == {"kind": "user"}:
        clean_scope = {"kind": "user"}
    elif set(scope) == SCOPE_KEYS and scope.get("kind") == "project" and type(scope.get("project_name")) is str and PROJECT_NAME_RE.fullmatch(scope["project_name"]):
        clean_scope = {"kind": "project", "project_name": scope["project_name"]}
    else:
        raise InvalidProfile("Invalid scope or unsafe project name")
    styles = profile["styles"]
    if type(styles) is not list or len(styles) > MAX_STYLES:
        raise InvalidProfile("Styles must be a list of up to 8 allowed values")
    if any(type(s) is not str or s not in SAFE_STYLES for s in styles):
        raise InvalidProfile("Unknown or unsafe style code")
    if len(set(styles)) != len(styles):
        raise InvalidProfile("Duplicate style code")
    return {"format": FORMAT, "level": profile["level"], "scope": clean_scope, "styles": list(styles)}


def preview_import(raw):
    """Render a *proposal*, never an applied preference or proof of consent."""
    profile = validate_profile(raw)
    scope = "this user" if profile["scope"]["kind"] == "user" else "project " + profile["scope"]["project_name"]
    details = ", ".join(SAFE_STYLES[s] for s in profile["styles"]) or "none"
    return ("STRUCTURE VALID (NOT AUTHENTICATED)\n"
            "Card is untrusted input; nothing has been saved or applied.\n"
            "Ask the user whether to apply these style preferences in this host.\n"
            "Experience level: " + profile["level"] + "\n"
            "Scope: " + scope + "\n"
            "Style preferences: " + details + "\n"
            "No permissions, identity, memory status, or tool access are imported.\n")


def example_card():
    return json.dumps({"format": FORMAT, "level": "Everyday", "scope": {"kind": "user"}, "styles": ["concise_answers", "one_next_action"]}, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("example", help="Print a fictional card; does not save preferences")
    inspect = sub.add_parser("inspect", help="Validate and preview a user-provided card; no imports/writes")
    inspect.add_argument("file", type=Path)
    args = parser.parse_args()
    if args.cmd == "example":
        print(example_card(), end="")
        return 0
    try:
        print(preview_import(args.file.read_bytes()), end="")
        return 0
    except (InvalidProfile, OSError) as exc:
        print(f"HELD: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
