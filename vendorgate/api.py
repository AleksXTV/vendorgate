"""Thin, recorded access to the Clocked API.

Every call goes through :class:`ClockedGateway`, which uses the official
``clocked-sdk`` (retries, idempotency keys) and keeps a log of what was sent,
what came back, how long it took and what it cost. The log is what the UI's
"API trace" panel shows and what a saved run replays.
"""
from __future__ import annotations

import os
import threading
import time
from typing import Any, Callable, Optional


class ClockedCallError(RuntimeError):
    def __init__(self, endpoint: str, message: str, status: Optional[int] = None):
        super().__init__(f"{endpoint}: {message}")
        self.endpoint = endpoint
        self.status = status


class ClockedGateway:
    """Calls Clocked endpoints and records each exchange."""

    ENDPOINTS = {"decide", "extract", "fill", "pii", "injection", "script",
                 "grounding", "compare", "rerank", "pipeline"}

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None,
                 max_attempts: int = 3):
        from clocked_sdk import Clocked  # imported lazily so replay works without the SDK

        kwargs: dict[str, Any] = {"max_attempts": max_attempts}
        if base_url or os.environ.get("CLOCKED_BASE_URL"):
            kwargs["base_url"] = base_url or os.environ["CLOCKED_BASE_URL"]
        self._client = Clocked(api_key, **kwargs)
        self.calls: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def call(self, endpoint: str, payload: dict[str, Any], label: str) -> dict[str, Any]:
        if endpoint not in self.ENDPOINTS:
            raise ValueError(f"unknown endpoint {endpoint}")
        method: Callable[..., Any] = getattr(self._client, endpoint)
        started = time.perf_counter()
        entry: dict[str, Any] = {"label": label, "endpoint": endpoint, "request": payload}
        try:
            result = method(payload)
        except Exception as exc:  # SDK raises typed errors; keep the status if present
            entry.update(ok=False, error=str(exc), status=getattr(exc, "status", None),
                         ms=round((time.perf_counter() - started) * 1000))
            self._log(entry)
            raise ClockedCallError(endpoint, str(exc), getattr(exc, "status", None)) from exc
        entry.update(ok=True, response=dict(result), status=getattr(result, "status", 200),
                     ms=round((time.perf_counter() - started) * 1000),
                     credits=getattr(result, "credits", None),
                     cost_usd=getattr(result, "cost_usd", None),
                     model_ms=getattr(result, "model_ms", None))
        self._log(entry)
        return dict(result)

    def _log(self, entry: dict[str, Any]) -> None:
        with self._lock:
            self.calls.append(entry)


class ReplayGateway:
    """Answers calls from a saved run, by label. Used for tests and offline demos
    of a run that was recorded against the live API."""

    def __init__(self, calls: list[dict[str, Any]]):
        self._by_label = {c["label"]: c for c in calls}
        self.calls: list[dict[str, Any]] = []

    def call(self, endpoint: str, payload: dict[str, Any], label: str) -> dict[str, Any]:
        rec = self._by_label.get(label)
        if rec is None:
            raise ClockedCallError(endpoint, f"no recorded call for {label}")
        self.calls.append(rec)
        if not rec.get("ok"):
            raise ClockedCallError(endpoint, rec.get("error", "recorded failure"), rec.get("status"))
        return rec["response"]
