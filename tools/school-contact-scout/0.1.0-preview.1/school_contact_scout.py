#!/usr/bin/env python3
"""School Contact Scout: refresh recorded public school-contact sources.

Python 3.9+ standard library only. No crawling, email guessing, messaging,
baseline changes, or outreach-ledger changes. See README.md.
"""
import argparse
import base64
import collections
import concurrent.futures
import csv
import datetime as dt
import gzip
import hashlib
import http.client
import io
import ipaddress
import json
import re
import socket
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
import urllib.request
import uuid
from html.parser import HTMLParser
from html import escape
from pathlib import Path
from unittest import mock

VERSION = "0.1.0-preview.1"
MAX_BYTES = 2 * 1024 * 1024
MAX_BASELINE_BYTES = 16 * 1024 * 1024
MAX_RECORDS = 10000
MAX_BASELINE_URLS = 1000
MAX_SOURCES_PER_RUN = 100
MAX_REDIRECTS = 4
MAX_ADDRESS_ATTEMPTS = 4
MAX_HTML_NODES = 25000
MAX_HTML_DEPTH = 64
MAX_EMAILS_PER_SOURCE = 10000
EMAIL = re.compile(r"(?<![\w.@+-])([A-Za-z0-9][A-Za-z0-9._%+-]*@[A-Za-z0-9][A-Za-z0-9.-]*\.[A-Za-z]{2,63})(?![\w@-])")
FULL_EMAIL = re.compile(r"[A-Za-z0-9][A-Za-z0-9._%+-]*@[A-Za-z0-9][A-Za-z0-9.-]*\.[A-Za-z]{2,63}")
SKIP = {"script", "style", "template"}
BLOCK = {"tr", "td", "th", "p", "div", "section", "li", "br", "h1", "h2", "h3"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class Node:
    def __init__(self, tag, attrs=(), parent=None):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs), parent, []

    def text(self):
        if self.tag in SKIP:
            return ""
        parts = []
        for child in self.children:
            if isinstance(child, str):
                parts.append(child)
            else:
                parts.append((" " if child.tag in BLOCK else "") + child.text() + (" " if child.tag in BLOCK else ""))
        return "".join(parts)

    def walk(self):
        if self.tag in SKIP:
            return
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()


class PublicHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = self.current = Node("root")
        self.node_count = self.depth = 0

    def handle_starttag(self, tag, attrs):
        self.node_count += 1
        if self.node_count > MAX_HTML_NODES or self.depth >= MAX_HTML_DEPTH:
            raise ValueError("HTML structure exceeds parser bounds")
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in VOID:
            self.current = node
            self.depth += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        node = self.current
        while node.parent:
            if node.tag == tag:
                self.current = node.parent
                self.depth = 0
                parent = self.current
                while parent.parent:
                    self.depth += 1
                    parent = parent.parent
                return
            node = node.parent

    def handle_data(self, data):
        self.current.children.append(data)


def clean(text):
    return re.sub(r"\s+", " ", text).strip()


def email_strings(text):
    return set(x.lower() for x in EMAIL.findall(text))


def context(node):
    parent = node
    while parent.parent and parent.tag not in {"tr", "p", "li"}:
        parent = parent.parent
    if not hasattr(parent, "_context_text"):
        parent._context_text = clean(parent.text())[:600]
    return parent._context_text


def parse_public_html(html):
    """Extract supplied public text/mailto and standard Joomla public mail widgets.

    Does not execute JavaScript or infer mailbox/name patterns. Conflicts remain
    conflicts even when one spelling looks obvious.
    """
    parser = PublicHTML()
    parser.feed(html)
    nodes = list(parser.root.walk())
    page_text = clean(parser.root.text())
    locations = {}
    for match in EMAIL.finditer(page_text):
        locations.setdefault(match.group(1).lower(), match.start(1))
    addresses = set(locations)
    if len(addresses) > MAX_EMAILS_PER_SOURCE:
        raise ValueError("Source exceeds unique-email parsing bound")
    evidence, conflicts, link_targets = {}, [], {}

    def add_conflict(displayed, targets, node):
        if displayed and targets and set(displayed) != set(targets):
            conflicts.append({"displayed": sorted(displayed), "linked": sorted(targets), "context": context(node)})

    for node in nodes:
        if node.tag == "a" and (node.attrs.get("href") or "").lower().startswith("mailto:"):
            raw = urllib.parse.unquote(node.attrs["href"][7:].split("?", 1)[0])
            targets = {x.strip().lower() for x in re.split(r"[,;]", raw) if x.strip()}
            displayed = email_strings(node.text())
            add_conflict(displayed, targets, node)
            for target in targets:
                if FULL_EMAIL.fullmatch(target):
                    addresses.add(target)
                    evidence.setdefault(target, context(node))
            link_targets[node] = targets
        if node.tag == "joomla-hidden-mail":
            try:
                first = base64.b64decode(node.attrs["first"], validate=True).decode("utf-8")
                last = base64.b64decode(node.attrs["last"], validate=True).decode("utf-8")
                target = (first + "@" + last).lower()
                shown = base64.b64decode(node.attrs.get("text", ""), validate=True).decode("utf-8")
                displayed = email_strings(shown)
                add_conflict(displayed, {target}, node)
                if FULL_EMAIL.fullmatch(target):
                    addresses.add(target)
                    evidence.setdefault(target, clean(shown) or "Public Joomla email widget")
                addresses.update(displayed)
            except (ValueError, KeyError, UnicodeError, TypeError):
                # Malformed widget stays unavailable; never reconstruct by guessing.
                pass
        if len(addresses) > MAX_EMAILS_PER_SOURCE:
            raise ValueError("Source exceeds unique-email parsing bound")
    # Also catch a name-linked mailto disagreeing with a separate single email
    # printed elsewhere in the same table row/paragraph. Multi-person rows are
    # not paired heuristically.
    for node in nodes:
        if node.tag not in {"tr", "p", "li"}:
            continue
        shown = email_strings(node.text())
        targets = set()
        for descendant in node.walk():
            targets.update(link_targets.get(descendant, ()))
        if len(shown) == 1 and len(targets) == 1:
            add_conflict(shown, targets, node)
        for email in shown:
            evidence.setdefault(email, clean(node.text())[:600])
    for email in addresses:
        if email not in evidence:
            pos = locations.get(email, -1)
            evidence[email] = page_text[max(0, pos - 130):pos + len(email) + 150] if pos >= 0 else "Public mailto or Joomla widget"
    dedup = {json.dumps(c, sort_keys=True): c for c in conflicts}
    return {"emails": sorted(addresses), "conflicts": list(dedup.values()), "evidence": evidence}


def validate_url(url, allowed_hosts=None):
    if not isinstance(url, str) or not url or len(url) > 2048:
        raise ValueError("Source URL must be a nonempty string of at most 2048 characters")
    if any(ord(char) <= 32 or ord(char) == 127 for char in url) or "\\" in url:
        raise ValueError("Whitespace, control characters and backslashes are not supported in source URLs")
    parsed = urllib.parse.urlsplit(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in {"https", "http"} or not host or parsed.username is not None or parsed.password is not None or parsed.fragment:
        raise ValueError("Unsupported public source URL")
    if parsed.port not in {None, 443 if parsed.scheme == "https" else 80}:
        raise ValueError("Only the scheme's standard HTTP/HTTPS port is supported")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        if len(host) > 253 or "." not in host or any(not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", part) for part in host.split(".")):
            raise ValueError("Source host must be a fully qualified ASCII DNS name; use punycode for international names")
        if host.endswith((".localhost", ".local", ".localdomain", ".internal", ".lan", ".home", ".invalid", ".test", ".example")):
            raise ValueError("Local or reserved host is not a public source")
    else:
        raise ValueError("IP-literal source hosts are not supported")
    if allowed_hosts is not None and host not in allowed_hosts:
        raise ValueError("Redirect/source host is not recorded in the baseline: " + host)
    return host


def public_address(address):
    ip = ipaddress.ip_address(address)
    mapped = getattr(ip, "ipv4_mapped", None)
    return bool(ip.is_global and not ip.is_multicast and not ip.is_reserved and (mapped is None or public_address(str(mapped))))


def open_public_socket(host, port, timeout):
    """Resolve once, reject any nonpublic answer, then connect to a vetted IP.

    Pinning the actual socket avoids the check-then-resolve DNS-rebinding gap.
    HTTP Host and TLS certificate/SNI checks still use the original hostname.
    """
    answers = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    if not answers:
        raise ValueError("Source hostname has no usable address")
    vetted = []
    for family, socktype, protocol, _, address in answers:
        if family not in {socket.AF_INET, socket.AF_INET6} or not public_address(address[0]):
            raise ValueError("Source DNS includes a nonpublic or unsupported address")
        key = (family, socktype, protocol, address)
        if key not in vetted:
            vetted.append(key)
    last_error = None
    for family, socktype, protocol, address in vetted[:MAX_ADDRESS_ATTEMPTS]:
        connection = socket.socket(family, socktype, protocol)
        try:
            connection.settimeout(timeout)
            connection.connect(address)
            return connection
        except OSError as error:
            connection.close()
            last_error = error
    raise last_error or OSError("No public source address could be reached")


class PublicHTTPConnection(http.client.HTTPConnection):
    def connect(self):
        if self._tunnel_host:
            raise ValueError("HTTP proxy tunnels are not supported")
        self.sock = open_public_socket(self.host, self.port, self.timeout)


class PublicHTTPSConnection(http.client.HTTPSConnection):
    def connect(self):
        if self._tunnel_host:
            raise ValueError("HTTPS proxy tunnels are not supported")
        connection = open_public_socket(self.host, self.port, self.timeout)
        try:
            self.sock = self._context.wrap_socket(connection, server_hostname=self.host)
        except Exception:
            connection.close()
            raise


class PublicHTTPHandler(urllib.request.HTTPHandler):
    def http_open(self, request):
        return self.do_open(PublicHTTPConnection, request)


class PublicHTTPSHandler(urllib.request.HTTPSHandler):
    def https_open(self, request):
        return self.do_open(PublicHTTPSConnection, request, context=self._context)


class RecordedHostRedirects(urllib.request.HTTPRedirectHandler):
    max_redirections, max_repeats = MAX_REDIRECTS, 2

    def __init__(self, hosts):
        self.hosts = hosts

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        target = urllib.parse.urljoin(request.full_url, newurl)
        validate_url(target, self.hosts)
        if urllib.parse.urlsplit(request.full_url).scheme == "https" and urllib.parse.urlsplit(target).scheme != "https":
            raise ValueError("HTTPS-to-HTTP redirect refused")
        followed = getattr(request, "scout_redirect_count", 0)
        if followed >= MAX_REDIRECTS:
            raise ValueError("Redirect limit reached")
        redirected = super().redirect_request(request, fp, code, msg, headers, target)
        if redirected is not None:
            redirected.scout_redirect_count = followed + 1
        return redirected

    def http_error_302(self, request, response, code, message, headers):
        # The standard handler drains redirect bodies with an unbounded read.
        # Redirect content is irrelevant here: validate the target, close the
        # response without reading its body, then follow the bounded request.
        try:
            location = headers.get("Location") or headers.get("URI")
            if not location:
                return None
            redirected = self.redirect_request(request, response, code, message, headers, location)
        finally:
            response.close()
        if redirected is None:
            return None
        return self.parent.open(redirected, timeout=request.timeout)

    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302
    http_error_308 = http_error_302


def public_opener(hosts):
    # Environment proxies would add a separate, unvetted DNS/connection path.
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), PublicHTTPHandler(), PublicHTTPSHandler(), RecordedHostRedirects(hosts))


def decode_body(body, encoding, charset="utf-8"):
    if len(body) > MAX_BYTES:
        raise ValueError("Response exceeds size limit")
    if encoding.lower() == "gzip" or body.startswith(b"\x1f\x8b"):
        with gzip.GzipFile(fileobj=io.BytesIO(body)) as zipped:
            body = zipped.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise ValueError("Decoded response exceeds size limit")
    return body.decode(charset or "utf-8", errors="replace")


def fetch_source(url, hosts, timeout=20):
    result = {"url": url, "status": "fetch_error", "final_url": "", "error": "", "emails": [], "conflicts": [], "evidence": {}}
    try:
        validate_url(url, hosts)
        opener = public_opener(hosts)
        request = urllib.request.Request(url, headers={"User-Agent": "School-Contact-Scout/" + VERSION + " (public directory refresh)", "Accept": "text/html,application/xhtml+xml,text/plain", "Accept-Encoding": "gzip"})
        with opener.open(request, timeout=timeout) as response:
            result["final_url"] = response.geturl()
            validate_url(result["final_url"], hosts)
            kind = response.headers.get_content_type()
            if kind not in {"text/html", "application/xhtml+xml", "text/plain"}:
                raise ValueError("Unsupported response type: " + kind)
            html = decode_body(response.read(MAX_BYTES + 1), response.headers.get("Content-Encoding", ""), response.headers.get_content_charset())
        if re.search(r"<title[^>]*>\s*(?:Just a moment|Access Denied|Sign in|Attention Required)", html, re.I):
            raise ValueError("A challenge/sign-in page was returned; no bypass attempted")
        result.update(parse_public_html(escape(html) if kind == "text/plain" else html))
        result.update(status="ok", content_sha256=hashlib.sha256(html.encode("utf-8")).hexdigest())
    except Exception as exc:
        result["error"] = type(exc).__name__ + ": " + str(exc)[:400]
    return result


def record_sources(record):
    urls = [record.get("source_url", ""), record.get("additional_source_url", "")]
    alternates = record.get("alternate_source_urls", [])
    if not isinstance(alternates, list) or any(not isinstance(url, str) for url in alternates):
        raise ValueError("alternate_source_urls must be an array of URL strings")
    if any(not isinstance(url, str) for url in urls):
        raise ValueError("source_url and additional_source_url must be URL strings")
    urls.extend(alternates)
    return list(dict.fromkeys(u for u in urls if isinstance(u, str) and u))


def read_baseline(path, demo=False):
    with path.open("rb") as stream:
        raw = stream.read(MAX_BASELINE_BYTES + 1)
    if len(raw) > MAX_BASELINE_BYTES:
        raise ValueError("Baseline exceeds 16 MiB limit")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Baseline must be a JSON object")
    if data.get("fictional_example") and not demo:
        raise ValueError("The fictional example is offline-only; use --demo")
    groups = [data.get("teachers", []), data.get("school_contacts", [])]
    if any(not isinstance(group, list) for group in groups):
        raise ValueError("teachers and school_contacts must be JSON arrays")
    records = groups[0] + groups[1]
    if not records or len(records) > MAX_RECORDS:
        raise ValueError("Baseline must contain 1–10000 accepted records")
    ids, urls = set(), []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Each baseline record must be a JSON object")
        rid, email = record.get("record_id"), record.get("email")
        if not isinstance(rid, str) or not rid.strip() or len(rid) > 128:
            raise ValueError("Every record needs a nonempty record_id of at most 128 characters")
        if rid in ids:
            raise ValueError("Duplicate baseline record IDs; refresh stopped")
        ids.add(rid)
        if not isinstance(email, str) or len(email) > 254 or not FULL_EMAIL.fullmatch(email):
            raise ValueError("Invalid baseline email for record " + rid)
        sources = record_sources(record)
        if not sources:
            raise ValueError("Every accepted record needs at least one explicit source URL")
        for url in sources:
            validate_url(url)
            if url not in urls:
                urls.append(url)
        if len(urls) > MAX_BASELINE_URLS:
            raise ValueError("Baseline exceeds 1000 unique source URLs")
    if not isinstance(data.get("reviews", []), list) or any(not isinstance(item, dict) for item in data.get("reviews", [])):
        raise ValueError("reviews must be an array of JSON objects")
    return raw, data, records, urls


DEMO_HTML = {
    "https://example.org/schools/north/staff": '<h1>Fictional North School</h1><p>Alex Example — teacher <a href="mailto:alex.teacher@example.org">alex.teacher@example.org</a></p><p>Office <a href="mailto:north.office@example.org">north.office@example.org</a></p><p>Unreviewed new listing: new.teacher@example.org</p><p>Casey Example <a href="mailto:casey.other@example.org">casey.teacher@example.org</a></p>',
    "https://example.org/schools/south/staff": '<h1>Fictional South School</h1><p>Alex Example — visiting teacher: alex.teacher@example.org</p>'
}


def demo_source(url):
    if url not in DEMO_HTML:
        raise ValueError("Offline demo contains no fixture for this source URL")
    return {"url": url, "status": "ok", "final_url": url, "error": "", **parse_public_html(DEMO_HTML[url]), "content_sha256": hashlib.sha256(DEMO_HTML[url].encode()).hexdigest(), "offline_fixture": True}


def check_record(record, results):
    email = record["email"].lower()
    urls = record_sources(record)
    checked = [results[u] for u in urls if u in results]
    present = [s["url"] for s in checked if s["status"] == "ok" and email in s["emails"]]
    conflicts = [{"source_url": s["url"], **c} for s in checked for c in s["conflicts"] if email in c["displayed"] or email in c["linked"]]
    errors = [{"source_url": s["url"], "error": s["error"]} for s in checked if s["status"] != "ok"]
    if not checked:
        status = "not_checked_limit"
    elif conflicts:
        status = "source_conflict"
    elif present:
        status = "still_published"
    elif errors:
        status = "indeterminate_fetch_error"
    elif len(checked) < len(urls):
        status = "incomplete_source_check"
    else:
        status = "not_found_on_recorded_sources"
    return {"status": status, "present_source_urls": present, "source_errors": errors, "source_conflicts": conflicts, "checked_source_count": len(checked), "recorded_source_count": len(urls)}


def safe_cell(value):
    value = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return "'" + value if value.lstrip().startswith(("=", "+", "-", "@")) else value


def write_csv(path, rows, fields):
    with path.open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: safe_cell(row.get(key, "")) for key in fields})


def run(args):
    baseline = Path(args.baseline).resolve()
    raw, data, records, urls = read_baseline(baseline, demo=args.demo)
    hosts = {validate_url(u) for u in urls}
    selected = list(dict.fromkeys(args.source_url)) if args.source_url else urls
    if any(u not in urls for u in selected):
        raise ValueError("--source-url must exactly match a recorded accepted-record source URL")
    if not 1 <= args.limit <= MAX_SOURCES_PER_RUN or not 1 <= args.workers <= 4 or not 1 <= args.timeout <= 20:
        raise ValueError("Request limits are outside supported bounds")
    selected = selected[:args.limit]
    started_dt = dt.datetime.now(dt.timezone.utc)
    started = started_dt.isoformat()
    checked_date = started_dt.date().isoformat()
    if args.demo:
        results = {url: demo_source(url) for url in selected}
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            results = {r["url"]: r for r in pool.map(lambda u: fetch_source(u, hosts, args.timeout), selected)}
    accepted = {r["email"].lower() for r in records}
    domains = {e.rsplit("@", 1)[1] for e in accepted}
    review_emails = set()
    for item in data.get("reviews", []):
        review_emails.update(email_strings(str(item.get("displayed_email", "")) + " " + str(item.get("linked_email", ""))))
    affiliations = collections.defaultdict(list)
    for r in records:
        affiliations[r["email"].lower()].append({k: r.get(k, "") for k in ("record_id", "school", "name", "role", "source_year", "source_url")})
    refresh = []
    for r in records:
        observation = check_record(r, results)
        refresh.append({"record_id": r["record_id"], "school": r.get("school", ""), "name": r.get("name", ""), "role": r.get("role", ""), "email": r["email"], "teacher_flag": r.get("teacher_flag", "Unknown"), "baseline_roster_year": r.get("source_year", ""), "baseline_checked_date": r.get("checked_date", ""), "refresh_checked_at_utc": started if observation["checked_source_count"] else "", "refresh_checked_date_utc": checked_date if observation["checked_source_count"] else "", **observation, "recorded_source_urls": record_sources(r), "all_baseline_affiliations": affiliations[r["email"].lower()], "baseline_record_snapshot": r})
    candidates = []
    for url, result in results.items():
        if result["status"] != "ok":
            continue
        for email in result["emails"]:
            if email in accepted or email.rsplit("@", 1)[-1] not in domains:
                continue
            conflicts = [c for c in result["conflicts"] if email in c["displayed"] or email in c["linked"]]
            candidates.append({"candidate_id": "CAND-" + hashlib.sha256((url + "\n" + email).encode()).hexdigest()[:12], "email": email, "source_url": url, "checked_at_utc": started, "checked_date_utc": checked_date, "candidate_kind": "previously_in_review" if email in review_emails else "new_to_accepted_baseline", "review_status": "UNREVIEWED — do not add or contact automatically", "source_conflicts": conflicts, "evidence_context": result["evidence"].get(email, ""), "role_and_identity": "Not established by this refresh"})
    target = Path(args.output_dir).resolve() / ("refresh_" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ_") + uuid.uuid4().hex[:8])
    target.mkdir(parents=True, exist_ok=False)
    write_csv(target / "refresh_records.csv", refresh, list(refresh[0]))
    write_csv(target / "unreviewed_candidates.csv", candidates, ["candidate_id", "email", "source_url", "checked_at_utc", "checked_date_utc", "candidate_kind", "review_status", "source_conflicts", "evidence_context", "role_and_identity"])
    with baseline.open("rb") as stream:
        baseline_unchanged = stream.read(MAX_BASELINE_BYTES + 1) == raw
    summary = {"tool_version": VERSION, "started_at_utc": started, "finished_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "baseline_path": str(baseline), "baseline_sha256": hashlib.sha256(raw).hexdigest(), "baseline_unchanged_during_run": baseline_unchanged, "output_directory": str(target), "accepted_record_count": len(records), "recorded_source_url_count": len(urls), "selected_source_url_count": len(selected), "allowed_redirect_hosts": sorted(hosts), "workers": args.workers, "per_request_timeout_seconds": args.timeout, "status_counts": dict(collections.Counter(r["status"] for r in refresh)), "unreviewed_candidate_count": len(candidates), "source_checks": [{k: v for k, v in r.items() if k not in {"emails", "evidence"}} | {"published_email_count": len(r["emails"])} for r in results.values()], "limits": ["Check time is not roster year or employment confirmation.", "Email publication is not delivery or consent verification.", "No name/role reassignment is made automatically.", "Not found means absent from successfully checked recorded sources, not departed employment.", "Candidate domains come from accepted baseline addresses; candidate role and identity require review.", "Original records, record IDs, multiple affiliations, outreach/consent/opt-out fields and notes remain unchanged in baseline; full record snapshots accompany observations.", "Only explicit accepted-record source URL fields are fetched; page links are never crawled. Redirects are limited to recorded source hosts, with no HTTPS downgrade."]}
    summary.update(baseline_unchanged_during_run=baseline_unchanged, checked_date_utc=checked_date, timezone="UTC", offline_demo=args.demo, maximum_redirects_per_source=MAX_REDIRECTS, maximum_http_requests=len(selected) * (1 + MAX_REDIRECTS), maximum_wire_and_decoded_bytes_per_source=MAX_BYTES)
    summary["limits"].extend(["Every source and redirect connection rejects nonpublic DNS addresses and connects directly to a vetted address; environment proxies are disabled.", "Only HTML, XHTML and plain text are parsed; arbitrary JavaScript/JSON, PDF documents and login/challenge pages are not supported.", "Socket timeouts apply per operation; OS DNS resolution has its own timeout and there is no strict wall-clock run deadline."])
    with (target / "run_summary.json").open("x", encoding="utf-8") as stream:
        json.dump(summary, stream, ensure_ascii=False, indent=2)
    print(json.dumps({k: summary[k] for k in ["output_directory", "baseline_unchanged_during_run", "accepted_record_count", "recorded_source_url_count", "selected_source_url_count", "status_counts", "unreviewed_candidate_count"]}, ensure_ascii=False, indent=2))
    return target


class OfflineChecks(unittest.TestCase):
    def test_public_text_mailto_and_script_exclusion(self):
        parsed = parse_public_html('<p>A <span>one@</span>example.org</p><a href="mailto:two@example.org?subject=Hello">Teacher Two</a><a href>Empty link</a><script>"hidden@example.org"</script>')
        self.assertEqual(set(parsed["emails"]), {"one@example.org", "two@example.org"})

    def test_display_link_conflict(self):
        parsed = parse_public_html('<tr><td>Teacher</td><td><a href="mailto:wrong@example.org">right@example.org</a></td></tr>')
        self.assertTrue(parsed["conflicts"])
        self.assertEqual(set(parsed["emails"]), {"wrong@example.org", "right@example.org"})

    def test_malformed_link_is_not_repaired(self):
        parsed = parse_public_html('<a href="mailto:name@@example.org">name@example.org</a>')
        self.assertEqual(parsed["emails"], ["name@example.org"])
        self.assertEqual(parsed["conflicts"][0]["linked"], ["name@@example.org"])

    def test_separate_cells_and_multi_person_rows(self):
        bad = parse_public_html('<tr><td><a href="mailto:a@example.org">A</a></td><td>b@example.org</td></tr>')
        good = parse_public_html('<tr><td><a href="mailto:a@example.org">A</a><a href="mailto:b@example.org">B</a></td><td>a@example.org b@example.org</td></tr>')
        self.assertTrue(bad["conflicts"])
        self.assertFalse(good["conflicts"])

    def test_standard_joomla_public_widget(self):
        enc = lambda s: base64.b64encode(s.encode()).decode()
        parsed = parse_public_html('<joomla-hidden-mail first="' + enc('office') + '" last="' + enc('example.org') + '" text="' + enc('office@example.org') + '"></joomla-hidden-mail>')
        self.assertEqual(parsed["emails"], ["office@example.org"])
        self.assertFalse(parsed["conflicts"])
        self.assertFalse(parse_public_html('<joomla-hidden-mail first="%%%" last="%%%"></joomla-hidden-mail>')["emails"])

    def test_arbitrary_script_and_json_are_excluded(self):
        fixture = '<script>var school_sites = [{"school_email":"office@example.org"}];</script><template>template@example.org</template><style>/* style@example.org */</style>'
        self.assertFalse(parse_public_html(fixture)["emails"])

    def test_fetch_error_absence_and_limit_are_distinct(self):
        record = {"email": "a@example.org", "source_url": "https://example.org/staff"}
        url = record["source_url"]
        absent = {"url": url, "status": "ok", "emails": [], "conflicts": [], "error": ""}
        failed = {**absent, "status": "fetch_error", "error": "timeout"}
        self.assertEqual(check_record(record, {})["status"], "not_checked_limit")
        self.assertEqual(check_record(record, {url: absent})["status"], "not_found_on_recorded_sources")
        self.assertEqual(check_record(record, {url: failed})["status"], "indeterminate_fetch_error")
        record["alternate_source_urls"] = ["https://example.org/contact"]
        self.assertEqual(check_record(record, {url: absent})["status"], "incomplete_source_check")

    def test_conflict_status_and_original_state_unchanged(self):
        record = {"record_id": "KEEP-123", "email": "a@example.org", "school": "A", "source_url": "https://example.org/staff", "outreach_status": "Opted out", "do_not_contact": True}
        before = json.dumps(record, sort_keys=True)
        source = {"url": record["source_url"], "status": "ok", "emails": ["a@example.org"], "conflicts": [{"displayed": ["a@example.org"], "linked": ["b@example.org"], "context": "Teacher"}], "error": ""}
        self.assertEqual(check_record(record, {source["url"]: source})["status"], "source_conflict")
        self.assertEqual(json.dumps(record, sort_keys=True), before)

    def test_redirect_host_and_https_boundaries(self):
        handler = RecordedHostRedirects({"example.org"})
        request = urllib.request.Request("https://example.org/staff")
        with self.assertRaises(ValueError):
            handler.redirect_request(request, None, 302, "", {}, "https://example.net/")
        with self.assertRaises(ValueError):
            handler.redirect_request(request, None, 302, "", {}, "http://example.org/")
        self.assertEqual(handler.redirect_request(request, None, 302, "", {}, "/new").full_url, "https://example.org/new")

    def test_gzip_and_csv_formula_safety(self):
        self.assertEqual(decode_body(gzip.compress(b"<p>Public</p>"), "gzip"), "<p>Public</p>")
        self.assertTrue(safe_cell(" =1+1").startswith("'"))
        self.assertEqual(safe_cell("teacher@example.org"), "teacher@example.org")

    def test_public_url_syntax_boundaries(self):
        self.assertEqual(validate_url("https://example.org/staff"), "example.org")
        for url in ["file:///etc/hosts", "ftp://example.org/", "https://localhost/", "https://staff.local/", "https://127.0.0.1/", "https://[::1]/", "https://user:pass@example.org/", "https://@example.org/", "https://example.org:8000/", "https://example.org:80/", "https://example.org/#fragment", "https://example.org/\npath", "https://example.org\\@localhost/", "https://example.org%00/"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_url(url)

    def test_private_or_mixed_dns_is_rejected_before_connect(self):
        public = (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.215.14", 443))
        for value in ["127.0.0.1", "10.1.2.3", "169.254.169.254", "192.168.1.1", "100.64.0.1", "224.0.0.1"]:
            private = (socket.AF_INET, socket.SOCK_STREAM, 6, "", (value, 443))
            with self.subTest(address=value), mock.patch.object(socket, "getaddrinfo", return_value=[public, private]), mock.patch.object(socket, "socket") as create:
                with self.assertRaises(ValueError):
                    open_public_socket("example.org", 443, 1)
                create.assert_not_called()
        self.assertFalse(public_address("::ffff:127.0.0.1"))
        self.assertFalse(public_address("fc00::1"))

    def test_dns_is_not_resolved_again_after_validation(self):
        public = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.215.14", 443))]
        rebound = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))]
        connection = mock.Mock()
        with mock.patch.object(socket, "getaddrinfo", side_effect=[public, rebound]) as resolve, mock.patch.object(socket, "socket", return_value=connection):
            self.assertIs(open_public_socket("example.org", 443, 1), connection)
            self.assertEqual(resolve.call_count, 1)
            connection.connect.assert_called_once_with(("93.184.215.14", 443))

    def test_connection_attempts_are_bounded(self):
        answers = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.215." + str(i), 443)) for i in range(10, 20)]
        connection = mock.Mock()
        connection.connect.side_effect = OSError("offline fixture failure")
        with mock.patch.object(socket, "getaddrinfo", return_value=answers), mock.patch.object(socket, "socket", return_value=connection) as create:
            with self.assertRaises(OSError):
                open_public_socket("example.org", 443, 1)
            self.assertEqual(create.call_count, MAX_ADDRESS_ATTEMPTS)
            self.assertEqual(connection.close.call_count, MAX_ADDRESS_ATTEMPTS)

    def test_redirect_count_is_bounded(self):
        handler = RecordedHostRedirects({"example.org"})
        request = urllib.request.Request("https://example.org/start")
        for i in range(MAX_REDIRECTS):
            request = handler.redirect_request(request, None, 302, "", {}, "/step" + str(i))
        with self.assertRaises(ValueError):
            handler.redirect_request(request, None, 302, "", {}, "/too-many")

    def test_redirect_bodies_are_closed_without_any_read(self):
        for code in (301, 302, 303, 307, 308):
            with self.subTest(code=code):
                handler = RecordedHostRedirects({"example.org"})
                handler.parent = mock.Mock()
                handler.parent.open.return_value = "offline-next-response"
                response = mock.Mock()
                response.read.side_effect = AssertionError("Redirect body must never be read")
                request = urllib.request.Request("https://example.org/start")
                request.timeout = 1
                result = getattr(handler, "http_error_" + str(code))(request, response, code, "Redirect", {"Location": "/next"})
                self.assertEqual(result, "offline-next-response")
                response.read.assert_not_called()
                response.close.assert_called_once_with()
                next_request = handler.parent.open.call_args.args[0]
                self.assertEqual(next_request.full_url, "https://example.org/next")
                self.assertEqual(next_request.scout_redirect_count, 1)
        response = mock.Mock()
        response.read.side_effect = AssertionError("Rejected redirect body must never be read")
        with self.assertRaises(ValueError):
            handler.http_error_302(request, response, 302, "Redirect", {"Location": "http://127.0.0.1/"})
        response.read.assert_not_called()
        response.close.assert_called_once_with()

    def test_proxy_environment_is_not_used(self):
        with mock.patch.object(urllib.request, "getproxies", side_effect=AssertionError("Environment proxies must not be consulted")):
            self.assertIsNotNone(public_opener({"example.org"}))

    def test_tls_keeps_certificate_validation_and_hostname(self):
        import ssl
        connection = PublicHTTPSConnection("example.org")
        self.assertTrue(connection._context.check_hostname)
        self.assertEqual(connection._context.verify_mode, ssl.CERT_REQUIRED)
        raw = mock.Mock()
        wrapped = mock.Mock()
        with mock.patch(__name__ + ".open_public_socket", return_value=raw), mock.patch.object(connection._context, "wrap_socket", return_value=wrapped) as wrap:
            connection.connect()
            wrap.assert_called_once_with(raw, server_hostname="example.org")
            self.assertIs(connection.sock, wrapped)

    def test_parser_and_decoded_size_bounds(self):
        with self.assertRaises(ValueError):
            parse_public_html("<div>" * (MAX_HTML_DEPTH + 1))
        with self.assertRaises(ValueError):
            decode_body(gzip.compress(b"x" * (MAX_BYTES + 1)), "gzip")
        with self.assertRaises(ValueError):
            decode_body(b"x" * (MAX_BYTES + 1), "")
        with self.assertRaises(ValueError):
            parse_public_html(" ".join("teacher" + str(i) + "@example.org" for i in range(MAX_EMAILS_PER_SOURCE + 1)))

    def test_baseline_validation_rejects_bad_shapes_and_duplicates(self):
        record = {"record_id": "EX-1", "email": "teacher@example.org", "source_url": "https://example.org/staff"}
        cases = [[], {"teachers": "wrong"}, {"teachers": [record, record]}, {"teachers": [{**record, "email": "invalid"}]}, {"teachers": [{**record, "alternate_source_urls": "https://example.org/other"}]}, {"teachers": [{**record, "source_url": ""}]}, {"teachers": [record], "reviews": ["wrong"]}]
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as temporary:
            path = Path(temporary) / "bad.json"
            for case in cases:
                path.write_text(json.dumps(case), encoding="utf-8")
                with self.subTest(case=case), self.assertRaises(ValueError):
                    read_baseline(path)

    def test_fictional_demo_end_to_end_without_network(self):
        here = Path(__file__).resolve().parent
        baseline = here / "example_baseline.json"
        before = baseline.read_bytes()
        with self.assertRaises(ValueError):
            read_baseline(baseline)
        with tempfile.TemporaryDirectory(dir=here) as temporary, mock.patch.object(socket, "getaddrinfo", side_effect=AssertionError("No demo network")), mock.patch(__name__ + ".fetch_source", side_effect=AssertionError("No demo fetch")), mock.patch("sys.stdout", new_callable=io.StringIO):
            result = run(argparse.Namespace(baseline=str(baseline), output_dir=temporary, demo=True, source_url=[], limit=20, workers=1, timeout=1))
            summary = json.loads((result / "run_summary.json").read_text())
            self.assertEqual(summary["status_counts"], {"still_published": 3, "source_conflict": 1, "not_found_on_recorded_sources": 1})
            self.assertEqual(summary["unreviewed_candidate_count"], 2)
            self.assertTrue(summary["offline_demo"])
            self.assertTrue(summary["baseline_unchanged_during_run"])
            with (result / "refresh_records.csv").open(encoding="utf-8-sig", newline="") as stream:
                records = list(csv.DictReader(stream))
            alex = next(r for r in records if r["record_id"] == "EX-001")
            self.assertEqual(len(json.loads(alex["all_baseline_affiliations"])), 2)
            snapshot = json.loads(alex["baseline_record_snapshot"])
            self.assertTrue(snapshot["do_not_contact"])
            self.assertEqual(snapshot["outreach_status"], "Opted out")
        self.assertEqual(baseline.read_bytes(), before)


def main():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", help="User-supplied accepted-contact JSON; required for live refresh.")
    parser.add_argument("--output-dir", default=str(here / "refresh_runs"))
    parser.add_argument("--limit", type=int, choices=range(1, MAX_SOURCES_PER_RUN + 1), default=20, metavar="1-100", help="Maximum recorded source URLs to fetch (default 20; hard maximum 100).")
    parser.add_argument("--source-url", action="append", default=[], help="Optional representative recorded URL; repeatable and must exactly match baseline.")
    parser.add_argument("--workers", type=int, choices=range(1, 5), default=2)
    parser.add_argument("--timeout", type=int, choices=range(1, 21), default=20)
    parser.add_argument("--self-test", action="store_true", help="Run offline parser/error-boundary checks; no network; reads only bundled fictional fixtures.")
    parser.add_argument("--demo", action="store_true", help="Run the bundled fictional example offline; no network requests.")
    parser.add_argument("--version", action="version", version="School Contact Scout " + VERSION)
    args = parser.parse_args()
    if args.self_test and (args.demo or args.baseline):
        parser.error("--self-test cannot be combined with --demo or --baseline")
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(OfflineChecks))
        return 0 if result.wasSuccessful() else 1
    if args.demo:
        if args.baseline:
            parser.error("--demo uses only the bundled fictional baseline; omit --baseline")
        args.baseline = str(here / "example_baseline.json")
    elif not args.baseline:
        parser.error("supply --baseline PATH for live refresh, or use --demo / --self-test offline")
    try:
        run(args)
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("Refresh stopped: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
