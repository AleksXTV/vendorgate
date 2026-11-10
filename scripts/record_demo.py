"""Record the demo video and screenshots from the running app (live Clocked API).

    CLOCKED_API_KEY=... python scripts/record_demo.py

Starts the app, drives it with Playwright (headless Chromium), and writes
demo/vendorgate-demo.mp4 and docs/screenshot-*.png. Every result on screen
comes from live Clocked requests made during the recording.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PORT = int(os.environ.get("DEMO_PORT", "8011"))
OUT = Path(os.environ.get("DEMO_OUT", ROOT / "demo"))
RAW = OUT / "raw"
SHOTS = Path(os.environ.get("SHOTS_OUT", ROOT / "docs"))

CAPTION_JS = """(t) => { let c = document.getElementById('cap'); if (!c) { c = document.createElement('div'); c.id = 'cap';
 c.style.cssText = 'position:fixed;left:50%;bottom:28px;transform:translateX(-50%);max-width:78%;background:rgba(20,20,20,.88);color:#fff;padding:12px 18px;border-radius:12px;font:600 19px/1.35 system-ui;z-index:99;text-align:center;box-shadow:0 6px 24px rgba(0,0,0,.25)';
 document.body.appendChild(c);} c.textContent = t; c.style.display = t ? 'block' : 'none'; }"""


def main() -> int:
    if not os.environ.get("CLOCKED_API_KEY"):
        print("Set CLOCKED_API_KEY first.", file=sys.stderr)
        return 2
    shutil.rmtree(RAW, ignore_errors=True)
    RAW.mkdir(parents=True)
    SHOTS.mkdir(parents=True, exist_ok=True)
    srv = subprocess.Popen([sys.executable, "-m", "uvicorn", "vendorgate.server:app", "--port", str(PORT),
                            "--log-level", "warning"], cwd=ROOT)
    try:
        time.sleep(2.5)
        with sync_playwright() as p:
            b = p.chromium.launch()
            ctx = b.new_context(viewport={"width": 1440, "height": 900}, record_video_dir=str(RAW),
                                record_video_size={"width": 1440, "height": 900})
            pg = ctx.new_page()
            cap = lambda t, wait=3.2: (pg.evaluate(CAPTION_JS, t), pg.wait_for_timeout(int(wait * 1000)))
            pg.goto(f"http://127.0.0.1:{PORT}/?sample=quickpixel")
            pg.wait_for_selector("#sampleTabs button")
            cap("VendorGate: a vendor sends a contract, a security questionnaire, a sales email and an install script.", 4)
            cap("Before anyone signs, VendorGate reviews the whole packet with 9 Clocked endpoints.", 3.5)
            pg.click("#docTabs button[data-k=questionnaire]"); pg.wait_for_timeout(600)
            pg.evaluate("document.getElementById('docEditor').scrollTop = 1e6")
            cap("This vendor hid an instruction for AI reviewers in its questionnaire…", 3.5)
            pg.click("#docTabs button[data-k=install_script]")
            cap("…and its install script does more than install.", 3)
            pg.click("#runLive")
            cap("Running a live review: 12 requests to the Clocked API.", 1)
            pg.wait_for_function("document.querySelector('#verdict h2') !== null", timeout=240000)
            cap("Verdict: rejected. Hard guardrails in code mean a model can make the decision stricter, never looser.", 4.5)
            pg.screenshot(path=str(SHOTS / "screenshot-quickpixel.png"))
            for i, text in [
                (0, "Guard caught the injection and quarantined it; Protect replaced names, emails and phones before any later step."),
                (1, "Inspect flagged the lines that disable auditd, collect secrets and upload them, without executing anything."),
                (6, "Decide checked every applicable policy requirement: meets, violates or not established."),
            ]:
                el = pg.locator(f"#stages details.stage >> nth={i}")
                el.evaluate("e => e.open = true"); el.scroll_into_view_if_needed()
                cap(text, 4.5)
            pg.evaluate("window.scrollTo(0,0)")
            pg.click("#sampleTabs button[data-id=northwind]")
            cap("A second vendor: a real-looking SaaS deal with subtler problems.", 3)
            pg.click("#runLive")
            pg.wait_for_function("document.querySelector('#verdict h2') !== null", timeout=240000)
            cap("No blockers, but conditions: the sales email and the contract disagree.", 4)
            pg.screenshot(path=str(SHOTS / "screenshot-northwind.png"))
            for i, text in [(4, "Compare found statements that conflict across the vendor's own documents."),
                            (5, "Verify checked each sales promise against the binding contract and questionnaire."),
                            (2, "Extract pulled every key term verbatim, with its exact position in the contract."),
                            (3, "Rerank chose which of our 12 policy requirements apply to this vendor, and why the rest do not."),
                            (8, "Fill drafted the board memo and vendor email; Verify then checked the memo against the evidence.")]:
                el = pg.locator(f"#stages details.stage >> nth={i}")
                el.evaluate("e => e.open = true"); el.scroll_into_view_if_needed()
                cap(text, 4.5)
            pg.screenshot(path=str(SHOTS / "screenshot-memo.png"), full_page=False)
            pg.evaluate("window.scrollTo(0,0)")
            pg.click("#sampleTabs button[data-id=lumen]")
            pg.click("#runLive")
            pg.wait_for_function("document.querySelector('#verdict h2') !== null", timeout=240000)
            cap("And a low-risk font licence goes straight through.", 3.5)
            pg.click("#traceBox summary"); pg.locator("#traceBox").scroll_into_view_if_needed()
            cap("Every request, response, latency and credit cost is in the trace. VendorGate: decide with evidence.", 5)
            ctx.close(); b.close()
        webm = next(RAW.glob("*.webm"))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(webm), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-crf", "23", "-movflags", "+faststart", str(OUT / "vendorgate-demo.mp4")], check=True)
        print("wrote", OUT / "vendorgate-demo.mp4")
    finally:
        srv.terminate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
