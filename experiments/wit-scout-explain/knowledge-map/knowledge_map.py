"""Read-only, one-hop topic routing. No search, fetching, or source execution."""
import argparse
import json
import unicodedata
from pathlib import Path, PurePosixPath

MAX_BYTES = 64 * 1024
STATES = {"documented", "experimental"}


def _norm(value):
    if not isinstance(value, str):
        raise ValueError("not text")
    if any(unicodedata.category(ch).startswith("C") for ch in value):
        raise ValueError("invalid control or invisible format character")
    value = " ".join(unicodedata.normalize("NFC", value.casefold()).split())
    if not value or len(value) > 120:
        raise ValueError("invalid text length")
    return value


def _strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate map key")
        result[key] = value
    return result


def resolve(raw, topic):
    index = json.loads(raw, object_pairs_hook=_strict_object)
    if not isinstance(index, dict) or set(index) != {"schema", "records"} or type(index["schema"]) is not int or index["schema"] != 1:
        raise ValueError("unsupported map schema")
    records = index["records"]
    if not isinstance(records, list) or not 1 <= len(records) <= 64:
        raise ValueError("invalid record count")
    query = _norm(topic)
    matches, seen = [], set()
    for rec in records:
        if not isinstance(rec, dict) or set(rec) != {"id", "aliases", "state", "source"}:
            raise ValueError("invalid record")
        uid = _norm(rec["id"])
        aliases = rec["aliases"]
        source = rec["source"]
        if (uid in seen or not isinstance(aliases, list) or not 1 <= len(aliases) <= 12
                or rec["state"] not in STATES or not isinstance(source, str)
                or not source or len(source) > 240 or "\\" in source
                or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/._-" for c in source)
                or PurePosixPath(source).is_absolute() or ".." in source.split("/")
                or "." in source.split("/") or "" in source.split("/")):
            raise ValueError("invalid record fields")
        seen.add(uid)
        if query in {_norm(alias) for alias in aliases} | {uid}:
            matches.append({k: rec[k] for k in ("id", "state", "source")})
    return {"status": {0: "UNKNOWN", 1: "ROUTED"}.get(len(matches), "AMBIGUOUS"),
            "matches": sorted(matches, key=lambda item: item["id"]),
            "scope": "declared local source pointers, not verification or approval"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic")
    args = parser.parse_args()
    path = Path(__file__).with_name("topics.json")
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("map byte limit exceeded")
        output = resolve(raw, args.topic)
    except (OSError, ValueError, TypeError, RecursionError):
        print(json.dumps({"status": "HOLD", "matches": []}))
        return 2
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
