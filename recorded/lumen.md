# Vendor review: Lumen Type Foundry

**Recommendation: APPROVE** · risk Low · model said `approve` at 99%

> Approve, as the vendor meets all applicable requirements and the P12 low-risk fast track applies

## Pipeline
- **Intake: Guard every document, mask personal data** (pipeline, injection, pii): 4 personal-data values masked before analysis; no prompt injection found.
- **Inspect the vendor's install script (never executed)** (script): Verdict: benign (benign administration, severity none); 0 lines flagged.
- **Extract key contract terms verbatim** (extract): 8 of 11 terms found with source positions; not stated: breach_notice, subprocessors, model_training.
- **Rerank the policy library: which requirements apply?** (rerank): 3 of 12 requirements apply: P12-low-risk-fast-track, P7-endpoint-agents, P6-auto-renewal.
- **Compare what the vendor told us across documents** (compare): 0 statements contradicted elsewhere in the packet (0 conflicting passage pairs).
- **Verify each sales promise against the binding documents** (grounding): 4 sales claims checked: 0 contradicted by the documents, 0 not backed by them.
- **Decide each applicable requirement: meets, violates, not established** (decide): 2 met, 0 violated, 0 not established.
- **Decide the recommendation, then apply hard guardrails** (decide): Model: approve (99%); final after guardrails: approve; risk Low.
- **Fill the board memo and vendor email, then Verify the memo** (fill, grounding): Memo drafted; self-check: 98% grounded, 0 line(s) flagged for a human to check.

## Policy requirements
| Requirement | Result | Confidence |
|---|---|---|
| P6-auto-renewal Auto-renewal and termination | meets | 94% |
| P7-endpoint-agents Software installed on our infrastructure | meets | 68% |

## Sales claims vs. binding documents
- [supported] Attached is the order for the Lumen Sans family (desktop + web licence, up to 50 users).
- [supported] The licence is a flat annual fee of USD 2,400.
- [supported] We do not receive or store any of your data; you simply download the font files.
- [supported] The licence can be cancelled at the end of any annual term with 30 days' notice.

## Findings behind the decision (generated, then checked by Verify)
The vendor provides a commercial font licence for marketing materials with an annual fee of USD 2,400.
The install script review was benign with no flagged lines.
The licensor does not receive, host, or process licensee data.
All four checked sales claims are supported by the binding documents

## Draft email to the vendor

The procurement review for the commercial font licence has been completed. Based on the provided documentation, the request is approved. The contract terms, including the annual fee of USD 2,400 and the effective date of 1 December 2026, are consistent with the submitted data. No security concerns were identified during the review of the installation script or data processing terms. Please proceed with the next steps in the onboarding process to ensure the licence is active by the effective date. We look forward to working with Lumen Type Foundry AB

_12 Clocked requests · 85 credits · 3.8 s_