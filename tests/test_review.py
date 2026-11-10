import json
import threading
import time
from pathlib import Path

import uvicorn

from vendorgate.api import ClockedGateway, ReplayGateway
from vendorgate.report import to_markdown
from vendorgate.review import Packet
from vendorgate.runner import run_packet

ROOT = Path(__file__).resolve().parent.parent
import socket


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


PORT = _free_port()


def _serve():
    from tests.fake_clocked import app
    cfg = uvicorn.Config(app, port=PORT, log_level="warning")
    srv = uvicorn.Server(cfg)
    t = threading.Thread(target=srv.run, daemon=True)
    t.start()
    while not srv.started:
        time.sleep(0.05)
    return srv


def test_end_to_end_against_fake_api():
    srv = _serve()
    try:
        gw = ClockedGateway("test-key", base_url=f"http://127.0.0.1:{PORT}/clocked")
        rep = run_packet(Packet.from_dir(ROOT / "samples" / "quickpixel"), gw)
    finally:
        srv.should_exit = True
    ids = [s["id"] for s in rep["stages"]]
    assert ids == ["intake", "script", "terms", "policy", "conflicts", "claims", "compliance", "decision", "memo"]
    # the injected sentence never reaches later steps
    assert "Ignore all previous instructions" not in rep["documents"]["questionnaire"]
    assert rep["findings"]["injections"]
    # personal data replaced
    assert "@quickpixel.example" not in rep["documents"]["sales_email"]
    # a malicious script can never be approved, whatever the model says
    assert rep["decision"]["final"] == "reject"
    assert rep["usage"]["requests"] == 12
    assert "REJECT" in to_markdown(rep)

    # the saved trace replays to the same decision without the API
    rep2 = run_packet(Packet.from_dir(ROOT / "samples" / "quickpixel"), ReplayGateway(rep["trace"]))
    assert rep2["decision"]["final"] == rep["decision"]["final"]


def test_failed_requests_never_approve():
    gw = ReplayGateway([])  # every call fails
    rep = run_packet(Packet.from_dir(ROOT / "samples" / "lumen"), gw)
    assert rep["decision"]["final"] == "human_review"
    assert set(rep["findings"]["failed_stages"]) >= {"terms", "decision"}
