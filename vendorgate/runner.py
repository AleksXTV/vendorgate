"""Run a review and save it (with the full API trace) as JSON."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable, Optional

from .review import Packet, Review, Reviewer


def run_packet(packet: Packet, gateway: Any, on_update: Optional[Callable[[dict[str, Any]], None]] = None,
               concurrency: int = 4) -> dict[str, Any]:
    started = time.time()

    def push(review: Review) -> None:
        if on_update:
            on_update(snapshot(review, gateway, started, running=True))

    review = Reviewer(gateway, on_update=push, concurrency=concurrency).run(packet)
    return snapshot(review, gateway, started, running=False)


def snapshot(review: Review, gateway: Any, started: float, running: bool) -> dict[str, Any]:
    d = review.to_dict()
    calls = list(getattr(gateway, "calls", []))
    d["trace"] = calls
    d["usage"] = {
        "requests": len(calls),
        "credits": sum(c.get("credits") or 0 for c in calls),
        "cost_usd": round(sum(c.get("cost_usd") or 0 for c in calls), 4),
        "wall_seconds": round(time.time() - started, 1),
    }
    d["running"] = running
    d["recorded_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    return d


def save(report: dict[str, Any], path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report, indent=1, ensure_ascii=False))
    return p
