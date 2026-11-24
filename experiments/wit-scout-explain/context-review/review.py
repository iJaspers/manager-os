"""Render a fictional demo or an already-authorized, anchored Scout checkpoint."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from _base import load_research_checkpoint
from demo_session import make_demo_session
from render_review import render_review
from review_view import build_review_view


def write_new(path, contents):
    """Write a new private file; refuse an existing file or final symlink."""
    fd = os.open(Path(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(contents)
        stream.flush()
        os.fsync(stream.fileno())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--demo", action="store_true", help="Use invented offline examples")
    modes.add_argument("--checkpoint", type=Path, help="Existing Scout research checkpoint")
    parser.add_argument("--expected-sha256", help="Digest retained outside the checkpoint")
    parser.add_argument("--code-revision", help="Host-approved expected code revision")
    parser.add_argument("--source", action="append", default=[], help="Host-approved source URL; repeat")
    parser.add_argument("--include-source-details", action="store_true",
                        help="Include source links and excerpts for the same authorized audience")
    parser.add_argument("--html", type=Path, help="New standalone HTML output path")
    args = parser.parse_args(argv)
    if args.demo:
        if args.expected_sha256 or args.code_revision or args.source:
            parser.error("Checkpoint anchors cannot be used with --demo")
        session = make_demo_session()
        origin = "SYNTHETIC_DEMO"
    else:
        if not args.expected_sha256 or not args.code_revision or not args.source:
            parser.error("Checkpoint mode requires external digest, code revision and allowed sources")
        session = load_research_checkpoint(
            args.checkpoint, expected_sha256=args.expected_sha256,
            expected_code_revision=args.code_revision, approved_urls=tuple(args.source))
        origin = "HOST_SESSION"
    report = build_review_view(session, include_source_details=args.include_source_details,
                               origin=origin)
    if args.html:
        write_new(args.html, render_review(report))
        print(json.dumps({"output": str(args.html), "verdict": report["verdict"],
                          "owner_confirmation": "NOT_VERIFIED", "origin": origin}))
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
