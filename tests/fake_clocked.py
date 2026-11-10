"""A tiny stand-in for the Clocked API, for tests only.

It returns responses with the documented shapes, produced by keyword
heuristics. It is NOT Clocked and its outputs are not model judgments; the
demo and the recorded runs in recorded/ come from the live API.
"""
from __future__ import annotations

import re
from typing import Any

from fastapi import FastAPI, Request

app = FastAPI()
INJ = re.compile(r"ignore (all )?previous instructions[^\n]*", re.I)


def _ok(d: dict) -> dict:
    return {"model": "fake-for-tests", **d}


def _guard(text: str) -> dict:
    m = INJ.search(text)
    if not m:
        return _ok({"injection": 0.01, "verdict": "benign", "category": "benign", "severity": "none", "evidence": []})
    return _ok({"injection": 0.99, "verdict": "injection", "category": "instruction override", "severity": "high",
                "evidence": [{"quote": m.group(0), "start": m.start(), "end": m.end(), "confidence": 1}]})


def _pii(text: str) -> dict:
    ents = [{"type": "email", "value": m.group(0), "start": m.start(), "end": m.end(), "confidence": 1}
            for m in re.finditer(r"[\w.]+@[\w.-]+", text)]
    out = text
    for e in sorted(ents, key=lambda e: -e["start"]):
        out = out[:e["start"]] + "<EMAIL>" + out[e["end"]:]
    return _ok({"entities": ents, "counts": {"email": len(ents)}, "anonymized_text": out})


@app.post("/clocked/{ep}")
async def ep(ep: str, req: Request) -> Any:
    b = await req.json()
    if ep == "pipeline":
        steps = []
        for i, s in enumerate(b["steps"]):
            name = next(k for k in s if k in ("injection", "pii"))
            res = _guard(b["text"]) if name == "injection" else _pii(b["text"])
            steps.append({"step": i, "endpoint": name, "name": s.get("name"), "status": 200, "ms": 1, "result": res})
        return _ok({"steps": steps, "stopped": None})
    if ep == "script":
        bad = [l for l in b["script"].splitlines() if re.search(r"auditd|shadow|\| ?bash|history -c", l)]
        return _ok({"verdict": "malicious" if bad else "benign", "category": "data exfiltration" if bad else "benign administration",
                    "severity": "critical" if bad else "none", "malicious": 0.99 if bad else 0.01, "suspicious": 0.99 if bad else 0.02,
                    "evidence": [{"line": l, "start": b["script"].find(l), "end": b["script"].find(l) + len(l), "confidence": 1} for l in bad]})
    if ep == "extract":
        t = b["text"]
        fields = {}
        for k, f in b["fields"].items():
            if f.get("list"):
                fields[k] = {"value": [], "items": []}
            else:
                m = re.search(r"Governing Law\.? ([^\n]+)", t) if k == "governing_law" else None
                fields[k] = {"value": m.group(1), "start": m.start(1), "end": m.end(1), "confidence": 1} if m else {"value": None}
        return _ok({"fields": fields})
    if ep == "rerank":
        return _ok({"results": [{"index": i, "id": d["id"], "action": "use" if i < 5 else "skip",
                                 "reason": None if i < 5 else "different_case", "relevance_score": 0.9 if i < 5 else 0.1}
                                for i, d in enumerate(b["documents"])]})
    if ep == "compare":
        return _ok({"verdict": "unrelated", "pairs": []})
    if ep == "grounding":
        claims = [c.strip() for c in re.split(r"\n- ", b["answer"]) if c.strip()][:5]
        return _ok({"grounded": 0.5, "verdict": "contradicted", "claims": [
            {"claim": c, "kind": "claim", "counted": True, "verdict": "not_stated", "supported": 0.2} for c in claims]})
    if ep == "decide":
        ans = {}
        for k, q in b["questions"].items():
            if q["type"] == "choice":
                labels = list(q["criteria"])
                ans[k] = {"type": "choice", "choice": labels[-1], "confidence": 0.8,
                          "probabilities": {l: (0.8 if l == labels[-1] else 0.2 / (len(labels) - 1)) for l in labels}}
            elif q["type"] == "score":
                ans[k] = {"type": "score", "score": 2.0, "legend": {str(i): l for i, l in enumerate(q["criteria"])},
                          "probabilities": {}, "confidence": 0.7}
            else:
                ans[k] = {"type": "noul", "noul": 0.3, "decision": False}
        return _ok({"answers": ans})
    if ep == "fill":
        return _ok({"fields": {k: {"value": (f"(fake {k})" if f["type"] == "generate" else True), "source": "generated"}
                               for k, f in b["fields"].items()}})
    return {"error": "unknown"}
