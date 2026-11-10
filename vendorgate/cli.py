"""Command line: python -m vendorgate review samples/northwind [--save recorded/northwind.json]"""
from __future__ import annotations

import argparse
import json
import os
import sys

from .api import ClockedGateway, ReplayGateway
from .report import to_markdown
from .review import Packet
from .runner import run_packet, save


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="vendorgate")
    sub = ap.add_subparsers(dest="cmd", required=True)
    rv = sub.add_parser("review", help="review a vendor packet folder")
    rv.add_argument("packet")
    rv.add_argument("--save", help="write the full JSON report (with API trace) here")
    rv.add_argument("--markdown", help="write a Markdown board memo here")
    rv.add_argument("--replay", help="answer API calls from a saved report instead of the live API")
    rv.add_argument("--concurrency", type=int, default=int(os.environ.get("CLOCKED_CONCURRENCY", "4")))
    a = ap.parse_args(argv)

    packet = Packet.from_dir(a.packet)
    if a.replay:
        gw = ReplayGateway(json.load(open(a.replay))["trace"])
    else:
        if not os.environ.get("CLOCKED_API_KEY"):
            print("Set CLOCKED_API_KEY (see .env.example).", file=sys.stderr)
            return 2
        gw = ClockedGateway()

    printed: set[str] = set()

    def progress(snap: dict) -> None:
        for st in snap["stages"]:
            if st["status"] != "running" and st["id"] not in printed:
                printed.add(st["id"])
                print(f"  [{st['status']:>6}] {st['title']}: {st['summary']}", file=sys.stderr)

    report = run_packet(packet, gw, on_update=progress, concurrency=a.concurrency)
    d = report["decision"]
    print(f"\n{packet.vendor['name']}: {d.get('final')} (risk {d.get('risk_tier')}); "
          f"{report['usage']['requests']} Clocked requests, {report['usage']['credits']} credits")
    if a.save:
        save(report, a.save)
    if a.markdown:
        open(a.markdown, "w").write(to_markdown(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
