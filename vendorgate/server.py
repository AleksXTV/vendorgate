"""Web app: uvicorn vendorgate.server:app --port 8000"""
from __future__ import annotations

import json
import os
import threading
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .api import ClockedGateway
from .report import to_markdown
from .review import ROOT, Packet
from .runner import run_packet, save

app = FastAPI(title="VendorGate")
app.mount("/static", StaticFiles(directory=ROOT / "web"), name="static")
JOBS: dict[str, dict[str, Any]] = {}
SAMPLES = ROOT / "samples"
RECORDED = ROOT / "recorded"
RUNS = ROOT / "runs"


class PacketIn(BaseModel):
    vendor: dict[str, Any]
    sales_email: str
    contract: str
    questionnaire: str
    install_script: str = ""


@app.get("/")
def index() -> FileResponse:
    return FileResponse(ROOT / "web" / "index.html")


@app.get("/api/config")
def config() -> dict[str, Any]:
    return {"live": bool(os.environ.get("CLOCKED_API_KEY"))}


@app.get("/api/samples")
def samples() -> list[dict[str, Any]]:
    out = []
    for d in sorted(SAMPLES.iterdir()):
        if (d / "vendor.json").exists():
            p = Packet.from_dir(d)
            out.append({"id": d.name, "vendor": p.vendor, **p.docs, "install_script": p.install_script,
                        "recorded": (RECORDED / f"{d.name}.json").exists()})
    return out


@app.get("/api/recorded/{name}")
def recorded(name: str) -> Any:
    f = RECORDED / f"{Path(name).name}.json"
    if not f.exists():
        raise HTTPException(404, "no recorded run")
    return json.loads(f.read_text())


@app.post("/api/reviews")
def start(p: PacketIn) -> dict[str, str]:
    if not os.environ.get("CLOCKED_API_KEY"):
        raise HTTPException(400, "Live mode needs CLOCKED_API_KEY on the server. Open a recorded run instead.")
    packet = Packet(vendor=p.vendor, docs={"sales_email": p.sales_email, "contract": p.contract,
                                          "questionnaire": p.questionnaire}, install_script=p.install_script)
    jid = uuid.uuid4().hex[:12]
    JOBS[jid] = {"running": True, "stages": [], "vendor": p.vendor}

    def work() -> None:
        try:
            gw = ClockedGateway()
            rep = run_packet(packet, gw, on_update=lambda s: JOBS.__setitem__(jid, s),
                             concurrency=int(os.environ.get("CLOCKED_CONCURRENCY", "4")))
            JOBS[jid] = rep
            save(rep, RUNS / f"{jid}.json")
        except Exception as exc:  # surface, never hide
            JOBS[jid] = {**JOBS.get(jid, {}), "running": False, "error": str(exc)}

    threading.Thread(target=work, daemon=True).start()
    return {"id": jid}


@app.get("/api/reviews/{jid}")
def status(jid: str) -> Any:
    if jid not in JOBS:
        raise HTTPException(404, "unknown review")
    return JOBS[jid]


@app.get("/api/reviews/{jid}/memo.md", response_class=PlainTextResponse)
def memo(jid: str) -> str:
    j = JOBS.get(jid)
    if not j or j.get("running"):
        raise HTTPException(404, "not finished")
    return to_markdown(j)
