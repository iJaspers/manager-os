"""Exercise the offline examples with local ChromeDriver and Python's standard library."""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
DRIVER = "http://127.0.0.1:9515"


def command(path, data=None, method=None):
    payload = None if data is None else json.dumps(data).encode()
    request = Request(DRIVER + path, data=payload, method=method,
                      headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=15) as response:
        return json.load(response)["value"]


@contextmanager
def chrome():
    with tempfile.TemporaryDirectory() as profile, subprocess.Popen(
        ["chromedriver", "--port=9515"], stdout=subprocess.DEVNULL
    ) as driver:
        try:
            for _ in range(60):
                try:
                    command("/status")
                    break
                except URLError:
                    if driver.poll() is not None:
                        raise RuntimeError("ChromeDriver exited")
                    time.sleep(0.1)
            result = command("/session", {"capabilities": {"alwaysMatch": {
                "browserName": "chrome", "goog:chromeOptions": {"args": [
                    "--headless=new", "--disable-dev-shm-usage", "--user-data-dir=" + profile
                ]}
            }}})
            session = "/session/" + result["sessionId"]
            try:
                yield session, result["capabilities"]["browserVersion"]
            finally:
                command(session, method="DELETE")
        finally:
            driver.terminate()


def check(session, width, page):
    def js(code, *args):
        return command(session + "/execute/sync", {"script": code, "args": args})

    def key(value):
        command(session + "/actions", {"actions": [{"type": "key", "id": "keyboard",
            "actions": [{"type": "keyDown", "value": value}, {"type": "keyUp", "value": value}]}]})

    def fits():
        assert js("return innerWidth === arguments[0] && "
                  "document.documentElement.scrollWidth <= innerWidth", width), "horizontal overflow"

    command(session + "/goog/cdp/execute", {"cmd": "Emulation.setDeviceMetricsOverride",
        "params": {"width": width, "height": 850, "deviceScaleFactor": 1, "mobile": False}})
    command(session + "/url", {"url": page.as_uri()})
    fits()
    links = js("return [...document.querySelectorAll('nav a')].map(a => a.hash)")
    assert links == ["#context", "#memories", "#limits"]
    for link in links:
        js("document.querySelector('nav a[href=\"'+arguments[0]+'\"]').click()", link)
        assert js("return location.hash === arguments[0] && "
                  "!!document.querySelector(arguments[0]).getClientRects().length", link)
    command(session + "/url", {"url": page.as_uri() + "?keyboard"})
    focused = set()
    for _ in range(100):
        key("\ue004")  # Tab
        tag = js("return document.activeElement.tagName")
        if tag == "A" and js("return !!document.activeElement.closest('nav')"):
            focused.add("nav")
        if tag != "SUMMARY":
            continue
        kind = js("return document.activeElement.closest('.proposal-card') ? 'proposal' : 'source'")
        assert js("return document.activeElement.matches(':focus-visible') && "
                  "getComputedStyle(document.activeElement).outlineStyle !== 'none'")
        key("\ue007")  # Enter
        assert js("return document.activeElement.parentElement.open")
        fits()
        key(" ")
        assert js("return !document.activeElement.parentElement.open")
        focused.add(kind)
        if focused == {"nav", "proposal", "source"}:
            break
    assert focused == {"nav", "proposal", "source"}, focused
    js("document.querySelectorAll('details').forEach(d=>d.open=true)")
    fits()
    body = js("return document.body.innerText")
    assert "Model usage unavailable" in body and "Owner confirmation: not verified" in body
    assert js("return !document.querySelector('form,button,input')")
    if page.name == "hold_review.html":
        assert "fetch failed" in body and "source not host fetched" in body
        assert "Hold for review" in js("return document.querySelector('.proposal-list').innerText")
    else:
        assert js("return [...document.querySelectorAll('.proposal-card .badge')].filter("
                  "e=>e.textContent.trim()==='Review required').length") == 5
    print(f"PASS {width}px {page.name} {hashlib.sha256(page.read_bytes()).hexdigest()}", flush=True)


if __name__ == "__main__":
    with chrome() as (session, version):
        print("Chrome", version, flush=True)
        for width in (1366, 390, 320):
            for name in ("incognide_review.html", "hold_review.html"):
                check(session, width, ROOT / "examples" / name)
