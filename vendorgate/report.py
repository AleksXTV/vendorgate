"""Render a review as a Markdown memo for the review board."""
from __future__ import annotations

from typing import Any

LABEL = {"approve": "APPROVE", "approve_with_conditions": "APPROVE WITH CONDITIONS",
         "escalate": "ESCALATE TO SECURITY / LEGAL", "reject": "REJECT", "human_review": "HUMAN REVIEW"}


def to_markdown(r: dict[str, Any]) -> str:
    v, d, f, m = r["vendor"], r["decision"], r["findings"], r.get("memo") or {}
    out = [f"# Vendor review: {v['name']}", "",
           f"**Recommendation: {LABEL.get(d.get('final'), d.get('final'))}** · risk {d.get('risk_tier')} · "
           f"model said `{d.get('model_choice')}` at {100 * (d.get('model_confidence') or 0):.0f}%"
           + (" · **human sign-off required**" if d.get("needs_human_signoff") else ""), ""]
    if m.get("headline"):
        out += [f"> {m['headline']}", ""]
    if d.get("guardrails"):
        out += ["## Guardrails applied", *[f"- {g}" for g in d["guardrails"]], ""]
    out += ["## Pipeline", *[f"- **{s['title']}** ({', '.join(s['endpoints'])}): {s['summary']}" for s in r["stages"]], ""]
    if f.get("compliance"):
        out += ["## Policy requirements", "| Requirement | Result | Confidence |", "|---|---|---|"]
        for pid, c in f["compliance"].items():
            out.append(f"| {pid} {c['title']} | {c['choice'].replace('_', ' ')} | {100 * (c.get('confidence') or 0):.0f}% |")
        out.append("")
    if f.get("conflicts"):
        out += ["## Conflicts between vendor documents"]
        for c in f["conflicts"]:
            out.append(f"- {c['a'].get('document')}: \"{c['a'].get('quote')}\" vs {c['b'].get('document')}: \"{c['b'].get('quote')}\"")
        out.append("")
    if f.get("claims"):
        out += ["## Sales claims vs. binding documents"]
        for c in f["claims"]:
            out.append(f"- [{c['verdict'].replace('_', ' ')}] {c['claim']}")
        out.append("")
    if m.get("rationale"):
        out += ["## Findings behind the decision (generated, then checked by Verify)", m["rationale"], ""]
    if m.get("asks"):
        out += ["## What to ask the vendor", m["asks"], ""]
    if m.get("unsupported_lines"):
        out += ["## Generated statements Verify could not ground (check by hand)", *[f"- {x}" for x in m["unsupported_lines"]], ""]
    if m.get("vendor_email"):
        out += ["## Draft email to the vendor", "", m["vendor_email"], ""]
    u = r.get("usage", {})
    out += [f"_{u.get('requests')} Clocked requests · {u.get('credits')} credits · {u.get('wall_seconds')} s_"]
    return "\n".join(out)
