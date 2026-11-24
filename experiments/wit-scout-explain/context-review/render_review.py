"""Offline HTML presentation for the derived WIT research-review view.

This module renders the caller's already-validated view. It is not an intake
endpoint, an authentication mechanism, or a memory writer. Every displayed
value is escaped anyway: source text remains untrusted even after retrieval.
"""
from __future__ import annotations

from html import escape
from urllib.parse import urlsplit


def _text(value, fallback="Not reported"):
    return escape(fallback if value is None else str(value), quote=True)


def _label(value):
    return _text(str(value or "not reported").replace("_", " ").lower())


def _number(value, *, positive=False):
    if type(value) is not int or value < (1 if positive else 0):
        return None
    return f"{value:,}"


def _link(url, label):
    """Render only explicit HTTP(S) destinations, never source-provided HTML."""
    if not isinstance(url, str) or any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in url):
        return _text(label)
    try:
        parsed = urlsplit(url)
        if (parsed.scheme not in ("https", "http") or not parsed.hostname or
                parsed.username is not None or parsed.password is not None or
                "\\" in url):
            return _text(label)
        parsed.port  # Reject malformed or out-of-range ports.
    except ValueError:
        return _text(label)
    return (f'<a href="{_text(url)}" target="_blank" rel="noopener noreferrer" '
            f'referrerpolicy="no-referrer">{_text(label)}</a>')


def _issues(issues):
    if not issues:
        return ""
    return '<ul class="issues">' + "".join(f"<li>{_label(item)}</li>" for item in issues) + "</ul>"


def _verdict(value):
    # Unknown strings can never create an approval-looking status.
    return ('<span class="badge hold">Hold for review</span>' if value == "HOLD"
            else '<span class="badge review">Review required</span>')


def _usage(usage, details_visible):
    count = _number(usage.get("input_tokens"))
    window = _number(usage.get("context_window"), positive=True)
    if usage.get("state") == "PROVIDER_REPORTED" and count is not None:
        measured = f'<strong>{count} input tokens</strong><span>Last request, as reported by the host.</span>'
        if window is not None:
            measured += f'<span>Reported model window: {window} tokens.</span>'
        if details_visible:
            measured += (f'<span class="small">Request: {_text(usage.get("request_id"))}<br>'
                         f'Reported at: {_text(usage.get("reported_at"))}</span>')
    else:
        measured = '<strong>Model usage unavailable</strong><span>No measured input-token count is available for this view.</span>'
    chars = _number(usage.get("evidence_characters"))
    estimate = _number(usage.get("evidence_tokens_estimate"))
    estimated = (f'<strong>~{estimate} tokens</strong>' if estimate is not None
                 else '<strong>Estimate unavailable</strong>')
    estimated += '<span>Rough source-text estimate; this is not the model’s prompt usage.</span>'
    if chars is not None:
        estimated += f'<span class="small">{chars} source-text characters.</span>'
    return ('<div class="usage-grid"><div class="usage-card"><h3>Model usage</h3>' + measured +
            '</div><div class="usage-card"><h3>Evidence size</h3>' + estimated + '</div></div>')


def _source(row):
    roles = ", ".join(str(item).replace("_", " ").lower() for item in row.get("used_for", []))
    coverage = {
        "COMPLETE_PINNED_FILE": "Complete file at a pinned revision",
        "FULL_PINNED_FILE": "Complete file at a pinned revision",
        "RETRIEVED_TEXT_COVERAGE_UNKNOWN": "Retrieved text; coverage unknown",
        "SNIPPET_ONLY": "Search snippet only",
        "NO_SOURCE_TEXT": "Source text unavailable",
    }.get(row.get("coverage"))
    coverage_html = _text(coverage) if coverage else _label(row.get("coverage"))
    return (
        '<article class="source-card">'
        f'<h3>{_text(row.get("title"))}</h3>'
        f'<p class="source-state">{coverage_html}</p>'
        f'<p>{_text(row.get("reason"))}</p>'
        f'<p class="small">Used for: {_text(roles, "Not reported")}</p>'
        '<details><summary>Source details</summary><div class="details-body">'
        f'<p class="source-link">{_link(row.get("url"), row.get("url") or "No source URL")}</p>'
        '<dl>'
        f'<dt>Retrieval</dt><dd>{_label(row.get("fetch_state"))}</dd>'
        f'<dt>Observed</dt><dd>{_text(row.get("observed_at"))}</dd>'
        f'<dt>Pinned revision</dt><dd><code>{_text(row.get("pinned_revision"))}</code></dd>'
        f'<dt>Content fingerprint</dt><dd><code>{_text(row.get("sha256"))}</code></dd>'
        '</dl>' + _issues(row.get("issues")) + '</div></details></article>'
    )


def _evidence(entry):
    matched = entry.get("evidence_state") == "MATCHED_HOST_TEXT"
    status = "Exact passage found in retained source text" if matched else "Source passage needs review"
    navigation = entry.get("navigation") or {}
    link = ""
    if matched and navigation.get("url"):
        link = '<p>' + _link(navigation["url"], "Open matched source") + '</p>'
    # The original source locator remains plainly labelled; a failed check is
    # not silently converted into a verified-navigation fallback.
    return (
        '<div class="evidence-item">'
        f'<p class="small evidence-state">{status}</p>'
        f'<blockquote>{_text(entry.get("quote"), "No passage supplied")}</blockquote>'
        f'<p class="small">Claimed source: <span class="source-locator">{_text(entry.get("source_url"))}</span></p>'
        + link + '</div>'
    )


def _proposal(row, details_visible):
    change = {"NEW": "New statement", "UNCHANGED": "Statement unchanged",
              "CHANGED": "Statement changed"}.get(row.get("change_state"), "Current statement")
    evidence = {"MATCHED_SOURCE_TEXT": "Source text matched; meaning still needs review.",
                "HOLD": "Evidence check is on hold.",
                "REVIEW_REQUIRED": "Evidence needs review."}.get(row.get("evidence_state"), "Evidence needs review.")
    prior = ""
    if row.get("previous_statement") is not None:
        prior = ('<details><summary>Previous wording</summary><div class="details-body">'
                 f'<p>{_text(row["previous_statement"])}</p></div></details>')
    proof = ""
    if details_visible:
        entries = row.get("evidence") or []
        proof = ('<details><summary>Evidence and source</summary><div class="details-body">' +
                 ("".join(_evidence(item) for item in entries) if entries
                  else '<p>No source passage is attached to this proposal.</p>') +
                 '</div></details>')
    return (
        '<article class="proposal-card">'
        f'<div class="card-heading"><span class="eyebrow">{_text(row.get("id"))} · {change}</span>{_verdict(row.get("verdict"))}</div>'
        f'<p class="statement">{_text(row.get("statement"))}</p>'
        f'<p class="small">{evidence}</p>' + _issues(row.get("issues")) + prior + proof + '</article>'
    )


_CSS = """
:root{color-scheme:light;--navy:#122b3b;--ink:#213947;--muted:#506775;--line:#d5e1e6;--teal:#086b68;--paper:#fff;--bg:#edf3f5}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:5rem}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
a{color:var(--teal);text-decoration-thickness:1px;text-underline-offset:3px;overflow-wrap:anywhere}a:focus-visible,summary:focus-visible{outline:3px solid #df9b24;outline-offset:4px}
main{width:min(100% - 28px,1000px);margin:28px auto 44px}header{padding:clamp(22px,5vw,46px);background:var(--navy);color:#fff;border-radius:18px 18px 0 0}header .eyebrow{color:#9bd9d3}h1{font-size:clamp(1.65rem,5vw,2.5rem);line-height:1.18;margin:12px 0 16px;max-width:780px}h2{font-size:1.4rem;line-height:1.3;margin:0 0 12px}h3{font-size:1rem;line-height:1.4;margin:0 0 9px}p{margin:0 0 12px}header p{max-width:780px;color:#d8e6ed}
nav{display:flex;gap:8px;flex-wrap:wrap;background:#fff;padding:12px 18px;border:1px solid var(--line);border-top:0}nav a{padding:7px 12px;text-decoration:none;font-weight:650;border-radius:6px}nav a:hover{background:#e7f3f1}.eyebrow{font-size:.74rem;font-weight:750;letter-spacing:.08em;text-transform:uppercase;overflow-wrap:anywhere}.badges,.card-heading{display:flex;align-items:center;gap:10px;flex-wrap:wrap}.badge{display:inline-block;font-size:.76rem;font-weight:700;line-height:1.4;padding:6px 10px;border-radius:5px}.review{background:#def3ef;color:#12534e}.hold{background:#fff0d4;color:#78500a}.origin{color:#d7e6ed;font-size:.82rem}
.section{padding:clamp(20px,4vw,34px);background:var(--paper);border:1px solid var(--line);border-top:0}.section:last-child{border-radius:0 0 18px 18px}.section-intro{color:var(--muted);max-width:80ch}.summary-strip{display:flex;gap:14px 28px;flex-wrap:wrap;margin:20px 0 0}.summary-strip span{font-size:.82rem;color:#cfdee6}.summary-strip strong{font-size:1.1rem;color:#fff;margin-right:6px}
.usage-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:22px 0}.usage-card{padding:17px 19px;background:#f3f7f9;border:1px solid var(--line);border-radius:10px;min-width:0}.usage-card h3{font-size:.75rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}.usage-card strong,.usage-card span{display:block}.usage-card strong{font-size:1.08rem;margin-bottom:4px}.usage-card span{font-size:.84rem;color:var(--muted)}
.source-list,.proposal-list{display:grid;gap:14px}.source-card,.proposal-card{padding:20px;border:1px solid var(--line);border-radius:10px;min-width:0}.source-card{border-left:4px solid #5d9e98}.source-state{font-size:.83rem;color:var(--teal);font-weight:650}.small{font-size:.82rem;color:var(--muted)}.notice{padding:14px 17px;background:#eef6f5;border-left:3px solid #4e918b;border-radius:0 6px 6px 0;font-size:.88rem;margin:20px 0}.notice strong{display:block;margin-bottom:4px}.statement{font-size:1.05rem;line-height:1.6;margin-top:12px}.card-heading{justify-content:space-between}.issues{font-size:.83rem;color:#765018;padding-left:20px;margin:10px 0 15px}.issues li{margin:4px 0}
details{border-top:1px solid var(--line);margin-top:12px}summary{cursor:pointer;min-height:44px;padding:12px 2px;font-weight:650;font-size:.84rem;color:var(--teal)}.details-body{padding:4px 0 3px}.details-body p:last-child{margin-bottom:5px}dl{display:grid;grid-template-columns:minmax(90px,130px) minmax(0,1fr);gap:6px 14px;font-size:.79rem;margin:14px 0}dt{color:var(--muted)}dd{margin:0;min-width:0}code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:.78rem}blockquote{margin:10px 0;padding:12px 15px;background:#f4f7f8;border-left:3px solid #9bafb9;font-size:.88rem;white-space:pre-wrap}.evidence-item+.evidence-item{margin-top:18px;padding-top:12px;border-top:1px dashed var(--line)}.source-link{font-size:.83rem}.empty{padding:20px;border:1px dashed var(--line);border-radius:8px;color:var(--muted)}.limitations{padding-left:20px;margin:0;color:var(--muted);font-size:.86rem}.limitations li{margin:8px 0}.binding{padding-top:18px;margin-top:18px;border-top:1px solid var(--line)}
h1,h2,h3,p,li,dd,code,span,blockquote{overflow-wrap:anywhere;word-break:normal;min-width:0}
@media(max-width:600px){main{width:calc(100% - 16px);margin:8px auto 24px}header{border-radius:12px 12px 0 0;padding:24px 20px}.section{padding:23px 17px}.usage-grid{grid-template-columns:minmax(0,1fr)}.source-card,.proposal-card{padding:17px}.card-heading{align-items:flex-start}.summary-strip{gap:9px 20px}nav{padding:9px 10px;gap:2px}nav a{font-size:.83rem;padding:8px}dl{grid-template-columns:1fr;gap:1px}dd{margin-bottom:9px}.section:last-child{border-radius:0 0 12px 12px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{body{background:#fff}main{width:100%;margin:0}header{border-radius:0}nav{display:none}.section{break-inside:avoid}.source-card,.proposal-card{break-inside:avoid}details{display:block}summary{display:none}details::details-content{display:block}}
"""


def render_review(report: dict) -> str:
    """Render a derived report without executing source text or writing state.

    Source details are shown only for the exact boolean True. Even if a caller
    accidentally includes detail rows in a summary report, the renderer omits
    those source names, locators, and excerpts. The remaining report can still
    contain private proposal text; this is not a public-redaction mechanism.
    """
    if not isinstance(report, dict):
        raise ValueError("derived review report required")
    details_visible = report.get("source_details_visible") is True
    context = report.get("context") or {}
    memories = report.get("memory_review") or {}
    proposals = memories.get("proposals") or []
    count = _number(context.get("source_count")) or "0"
    title = _text(report.get("title"), "WIT research review")
    origins = {"SYNTHETIC_DEMO": "Fictional example",
               "HOST_SOURCE_REPLAY": "Replay of host-read sources",
               "HOST_SESSION": "Host research session"}
    origin = origins.get(report.get("origin"), "Source origin not reported")
    source_rows = context.get("sources") or []
    if not details_visible:
        sources_html = '<p class="empty">Source details are hidden in this summary. Open a detailed view only for an audience allowed to see the underlying material.</p>'
    elif source_rows:
        sources_html = '<div class="source-list">' + "".join(_source(row) for row in source_rows) + '</div>'
    else:
        sources_html = '<p class="empty">No sources are recorded for this view.</p>'
    proposals_html = ('<div class="proposal-list">' + "".join(_proposal(row, details_visible) for row in proposals) + '</div>'
                      if proposals else '<p class="empty">No proposed memories are recorded for this view.</p>')
    limitations = []
    for group in (report.get("limitations"), context.get("limitations"), memories.get("limitations")):
        for item in group or []:
            if item not in limitations:
                limitations.append(item)
    limitation_html = ('<ul class="limitations">' + "".join(f"<li>{_text(item)}</li>" for item in limitations) + '</ul>'
                       if limitations else '<p class="small">Source matching does not establish truth, human approval, or completed actions.</p>')
    binding = report.get("review_binding") or {}
    binding_state = {"NEW": "New evidence bundle", "UNCHANGED": "Evidence bundle unchanged",
                     "INPUTS_CHANGED": "Evidence bundle changed; review again"}.get(binding.get("state"), "Evidence change state unavailable")
    changed_badge = ('<span class="badge hold">Evidence changed; review again</span>'
                     if binding.get("state") == "INPUTS_CHANGED" else "")
    binding_html = (f'<div class="binding small"><strong>{binding_state}</strong><br>'
                    f'View binding: <code>{_text(binding.get("sha256"))}</code><br>'
                    'A fingerprint detects changed input. It does not authenticate a person or grant permission.</div>')
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta name="referrer" content="no-referrer">'
        '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'">'
        f'<title>{title}</title><style>{_CSS}</style></head><body><main>'
        '<header><div class="eyebrow">WIT · Read-only research view</div>'
        f'<h1>{title}</h1><p>{_text(report.get("goal"), "Review the sources and proposed memories.")}</p>'
        f'<div class="badges">{_verdict(report.get("verdict"))}{changed_badge}<span class="origin">{origin}</span></div>'
        f'<div class="summary-strip"><span><strong>{count}</strong> sources in scope</span>'
        f'<span><strong>{len(proposals)}</strong> proposals to inspect</span></div></header>'
        '<nav aria-label="Review sections"><a href="#context">What WIT used</a><a href="#memories">Proposed memories</a><a href="#limits">Limits</a></nav>'
        '<section id="context" class="section"><h2>What WIT used</h2>'
        f'<p class="section-intro">{_text(context.get("scope"), "Sources represented in this research handoff.")}</p>'
        + _usage(context.get("usage") or {}, details_visible) + sources_html + '</section>'
        '<section id="memories" class="section"><h2>Proposed memories</h2>'
        '<p class="section-intro">These proposals are a view of existing research records. Reading this page does not save a memory or change a decision.</p>'
        '<div class="notice"><strong>Owner confirmation: not verified</strong>'
        'A source match or an AI-written status cannot confirm owner approval. This view grants no permission to act.</div>'
        + proposals_html + '</section>'
        '<section id="limits" class="section"><h2>Limits of this review</h2>'
        + limitation_html + binding_html + '</section></main></body></html>'
    )
