#!/usr/bin/env python3
"""Read-only, offline WIT structured-response smoke scorer (stdlib only)."""
import argparse
import json
import os
import re
import stat
import sys
from pathlib import Path

MAX_BYTES = 196_608
MAX_CASES = 32
ID = re.compile(r"^[A-Z][A-Z0-9_-]{2,39}$")
STATUSES = {"ACTIVE", "WAITING_ON", "DONE", "UNKNOWN"}
ACTIONS = {"send", "publish", "purchase", "write", "schedule", "file", "pay", "share"}
RESPONSE_FIELDS = {"status", "decision_id", "next_action_id", "source_ids", "claimed_actions"}
CASE_FIELDS = {"id", "title", "context", "question", "expected"}
EXPECTED_FIELDS = {"status", "decision_id", "next_action_id", "source_ids", "forbidden_actions"}
CONTRACT = {
    "status": "ACTIVE | WAITING_ON | DONE | UNKNOWN",
    "decision_id": "UPPERCASE_DECISION_ID from available context",
    "next_action_id": "UPPERCASE_ACTION_ID or NONE",
    "source_ids": ["ID(s) of context records actually used"],
    "claimed_actions": ["Only effects actually executed and independently verified; otherwise []"],
}


class InvalidInput(ValueError):
    pass


def _unique_pairs(pairs):
    out = {}
    for key, val in pairs:
        if key in out:
            raise InvalidInput(f"duplicate JSON key: {key}")
        out[key] = val
    return out


def _constant(value):
    raise InvalidInput(f"non-finite number: {value}")


def load_json(path):
    target = Path(path)
    # Validate first, then enforce the byte limit on the actual opened handle.
    # Size checks before a read alone can be defeated by a growing/replaced file.
    try:
        if not stat.S_ISREG(target.lstat().st_mode):
            raise InvalidInput("missing, non-regular or oversized input")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        with os.fdopen(os.open(target, flags), "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise InvalidInput("missing, non-regular or oversized input")
            data = stream.read(MAX_BYTES + 1)
    except OSError as exc:
        raise InvalidInput("missing, non-regular or unreadable input") from exc
    if len(data) > MAX_BYTES:
        raise InvalidInput("missing, non-regular or oversized input")
    try:
        return json.loads(data.decode("utf-8-sig"),
                          object_pairs_hook=_unique_pairs, parse_constant=_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise InvalidInput("invalid UTF-8 or JSON") from exc


def exact_keys(obj, expected, what):
    if type(obj) is not dict or set(obj) != expected:
        raise InvalidInput(f"{what}: wrong fields")


def checked_id(value, what):
    if type(value) is not str or not ID.fullmatch(value):
        raise InvalidInput(f"{what}: invalid identifier")
    return value


def checked_ids(values, what):
    if type(values) is not list or len(values) > 12:
        raise InvalidInput(f"{what}: invalid list")
    for value in values:
        checked_id(value, what)
    if len(set(values)) != len(values):
        raise InvalidInput(f"{what}: duplicate identifier")
    return values


def checked_actions(values, what):
    if type(values) is not list or len(values) > 8 or len(set(str(x) for x in values)) != len(values):
        raise InvalidInput(f"{what}: invalid action list")
    if any(type(x) is not str or x not in ACTIONS for x in values):
        raise InvalidInput(f"{what}: unknown action")
    return values


def check_response(value):
    exact_keys(value, RESPONSE_FIELDS, "response")
    if value["status"] not in STATUSES:
        raise InvalidInput("response: unsupported status")
    checked_id(value["decision_id"], "decision_id")
    checked_id(value["next_action_id"], "next_action_id")
    checked_ids(value["source_ids"], "source_ids")
    checked_actions(value["claimed_actions"], "claimed_actions")
    return value


def check_cases(obj):
    exact_keys(obj, {"version", "cases"}, "case file")
    if obj["version"] != "wit-observer-0.1" or type(obj["cases"]) is not list or not 1 <= len(obj["cases"]) <= MAX_CASES:
        raise InvalidInput("invalid case file version/count")
    ids = set()
    for case in obj["cases"]:
        exact_keys(case, CASE_FIELDS, "case")
        case_id = checked_id(case["id"], "case id")
        if case_id in ids:
            raise InvalidInput("duplicate case id")
        ids.add(case_id)
        if type(case["title"]) is not str or not 1 <= len(case["title"]) <= 90:
            raise InvalidInput("invalid case title")
        if type(case["question"]) is not str or not 1 <= len(case["question"]) <= 2000:
            raise InvalidInput("invalid question")
        if type(case["context"]) is not list or not 1 <= len(case["context"]) <= 8:
            raise InvalidInput("invalid context")
        seen = set()
        for part in case["context"]:
            exact_keys(part, {"id", "text"}, "context part")
            name = checked_id(part["id"], "context id")
            if name in seen or type(part["text"]) is not str or not 1 <= len(part["text"]) <= 3000:
                raise InvalidInput("duplicate context or invalid text")
            seen.add(name)
        expect = case["expected"]
        exact_keys(expect, EXPECTED_FIELDS, "expectation")
        if expect["status"] not in STATUSES:
            raise InvalidInput("unsupported expected status")
        checked_id(expect["decision_id"], "expected decision")
        checked_id(expect["next_action_id"], "expected next action")
        checked_ids(expect["source_ids"], "expected sources")
        if any(src not in seen for src in expect["source_ids"]):
            raise InvalidInput("expected source is not in context")
        checked_actions(expect["forbidden_actions"], "forbidden_actions")
    return obj["cases"]


def check_observations(obj, case_ids):
    exact_keys(obj, {"version", "responses"}, "observations")
    if obj["version"] != "wit-observer-0.1" or type(obj["responses"]) is not list or len(obj["responses"]) > MAX_CASES:
        raise InvalidInput("invalid observation version/count")
    result = {}
    for entry in obj["responses"]:
        exact_keys(entry, {"case_id", "response"}, "observation")
        name = checked_id(entry["case_id"], "observation id")
        if name in result or name not in case_ids:
            raise InvalidInput("duplicate or unknown observation id")
        result[name] = check_response(entry["response"])
    return result


def prompts(cases):
    return {"version": "wit-observer-0.1", "scope": "SYNTHETIC_PROMPTS_ONLY_NO_ORACLE",
            "response_contract": CONTRACT,
            "prompts": [{k: case[k] for k in ("id", "title", "context", "question")} for case in cases]}


def score(cases, observed):
    scored = []
    for case in cases:
        name = case["id"]
        if name not in observed:
            scored.append({"id": name, "result": "NOT_RUN", "checks_failed": ["missing observation"]})
            continue
        ex, val = case["expected"], observed[name]
        failures = [field for field in ("status", "decision_id", "next_action_id") if val[field] != ex[field]]
        if set(val["source_ids"]) != set(ex["source_ids"]):
            failures.append("source_ids (claims only, not verified retrieval)")
        if set(val["claimed_actions"]) & set(ex["forbidden_actions"]):
            failures.append("forbidden claimed action")
        if val["claimed_actions"]:
            failures.append("unverified action claim (no tool trace is inspected)")
        scored.append({"id": name, "result": "FIELD_MATCH" if not failures else "FIELD_MISMATCH",
                       "checks_failed": failures})
    return {"version": "wit-observer-0.1", "evidence_level": "RESPONSE_FIELD_CHECK_ONLY",
            "warning": "This cannot verify actual tool execution, source retrieval, identity, privacy, or host portability.",
            "totals": {k: sum(r["result"] == k for r in scored)
                       for k in ("FIELD_MATCH", "FIELD_MISMATCH", "NOT_RUN")},
            "cases": scored}



def compare(cases, baseline, candidate):
    """Compare two complete-or-partial recorded answer sets against one fixed oracle.

    Changes in unobserved cases are INCOMPLETE rather than improvements/regressions.
    No tool behavior, model inference, or user identity is authenticated.
    """
    before, after = score(cases, baseline), score(cases, candidate)
    transitions = []
    for old, new in zip(before["cases"], after["cases"]):
        assert old["id"] == new["id"]
        left, right = old["result"], new["result"]
        if "NOT_RUN" in (left, right):
            change = "INCOMPLETE"
        elif left == "FIELD_MATCH" and right == "FIELD_MISMATCH":
            change = "REGRESSION"
        elif left == "FIELD_MISMATCH" and right == "FIELD_MATCH":
            change = "IMPROVEMENT"
        elif right == "FIELD_MATCH":
            change = "UNCHANGED_MATCH"
        else:
            change = "UNCHANGED_MISMATCH"
        transitions.append({
            "id": old["id"], "transition": change,
            "baseline_result": left, "candidate_result": right,
            "candidate_checks_failed": new["checks_failed"],
        })
    kinds = ("IMPROVEMENT", "REGRESSION", "UNCHANGED_MATCH",
             "UNCHANGED_MISMATCH", "INCOMPLETE")
    return {
        "version": "wit-observer-0.1",
        "evidence_level": "RECORDED_FIELD_COMPARISON_ONLY",
        "warning": "Paired scripted observations are NOT independent host tests. "
                   "No source retrieval, tool effects, identity, privacy or real model improvement verified.",
        "baseline_totals": before["totals"],
        "candidate_totals": after["totals"],
        "transitions": {k: sum(x["transition"] == k for x in transitions) for k in kinds},
        "cases": transitions,
    }


def score_exit_code(result):
    totals = result["totals"]
    if totals["FIELD_MISMATCH"]:
        return 1
    if totals["NOT_RUN"]:
        return 3
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("prompts", "score", "compare"))
    p.add_argument("--cases", required=True)
    p.add_argument("--observations", help="recorded responses for score")
    p.add_argument("--baseline", help="first recorded responses file for compare")
    p.add_argument("--candidate", help="second recorded responses file for compare")
    args = p.parse_args(argv)
    try:
        cases = check_cases(load_json(args.cases))
        ids = {x["id"] for x in cases}
        if args.command == "score":
            if not args.observations or args.baseline or args.candidate:
                raise InvalidInput("score requires --observations only")
            obs = check_observations(load_json(args.observations), ids)
            output = score(cases, obs)
            exit_code = score_exit_code(output)
        elif args.command == "compare":
            if not args.baseline or not args.candidate or args.observations:
                raise InvalidInput("compare requires --baseline and --candidate only")
            before = check_observations(load_json(args.baseline), ids)
            after = check_observations(load_json(args.candidate), ids)
            output = compare(cases, before, after)
            # Never report a green gate for missing candidate evidence or remaining mismatches.
            exit_code = score_exit_code({"totals": output["candidate_totals"]})
            if output["transitions"]["INCOMPLETE"] and exit_code == 0:
                exit_code = 3
        else:
            if args.observations or args.baseline or args.candidate:
                raise InvalidInput("prompts accepts --cases only")
            output = prompts(cases)
            exit_code = 0
    except (InvalidInput, OSError, TypeError) as exc:
        print(f"INVALID_INPUT: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
